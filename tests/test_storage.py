import sqlite3
from pathlib import Path

import pytest

from founder_company_ai.models import (
    ActionStatus,
    MemoryCategory,
    RiskLevel,
    Scope,
    TaskStatus,
    Visibility,
)
from founder_company_ai.storage import SQLiteStore


def test_store_persists_structured_state(tmp_path: Path) -> None:
    database = tmp_path / "assistant.sqlite3"
    store = SQLiteStore(database)
    context = store.upsert_context(
        domain=Scope.COMPANY,
        key="company_name",
        value="EcoFixer",
        visibility=Visibility.COMPANY,
    )
    memory = store.add_memory(
        content="金額與抽成比例必須可設定",
        scope=Scope.PROJECT,
        category=MemoryCategory.DECISION,
        visibility=Visibility.PROJECT,
        project="EcoFixer AI OS",
    )
    task = store.add_task(
        title="完成權限模型",
        scope=Scope.COMPANY,
        priority=1,
    )
    store.add_message(
        conversation_id="founder-main",
        role="user",
        content="今天要做什麼？",
        cloud_allowed=True,
    )
    store.log_activity(
        action_type="test",
        summary="Test audit event",
        risk_level=RiskLevel.READ_ONLY,
    )

    reopened = SQLiteStore(database)

    assert reopened.list_context()[0].id == context.id
    assert reopened.list_memories()[0].id == memory.id
    assert reopened.list_tasks()[0].id == task.id
    assert reopened.list_messages("founder-main")[0].content == "今天要做什麼？"
    assert reopened.list_activity()[0].action_type == "test"


def test_context_upsert_keeps_identity_and_updates_value(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    first = store.upsert_context(
        domain=Scope.COMPANY,
        key="priority",
        value="iOS first",
        visibility=Visibility.COMPANY,
    )
    second = store.upsert_context(
        domain=Scope.COMPANY,
        key="priority",
        value="iOS release first",
        visibility=Visibility.COMPANY,
    )

    assert second.id == first.id
    assert store.list_context()[0].value == "iOS release first"


def test_founder_context_and_memory_cannot_be_company_visible(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")

    with pytest.raises(ValueError, match="founder-only"):
        store.upsert_context(
            domain=Scope.FOUNDER,
            key="private_preference",
            value="Private",
            visibility=Visibility.COMPANY,
        )

    with pytest.raises(ValueError, match="founder-only"):
        store.add_memory(
            content="Private founder note",
            scope=Scope.FOUNDER,
            category=MemoryCategory.NOTE,
            visibility=Visibility.COMPANY,
        )


def test_updates_task_status(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    task = store.add_task(title="Review", scope=Scope.FOUNDER)

    store.update_task_status(task.id, TaskStatus.DONE)

    assert store.list_tasks()[0].status is TaskStatus.DONE


def test_action_approval_and_prohibited_guard(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    merge = store.create_action_request(
        title="Merge PR",
        description="Merge a reviewed pull request",
        risk_level=RiskLevel.APPROVAL_REQUIRED,
    )
    prohibited = store.create_action_request(
        title="Delete production database",
        description="Delete production database without authorization",
        risk_level=RiskLevel.PROHIBITED,
    )

    store.update_action_status(merge.id, ActionStatus.APPROVED)

    requests = {item.id: item for item in store.list_action_requests()}
    assert requests[merge.id].status is ActionStatus.APPROVED
    assert requests[prohibited.id].status is ActionStatus.BLOCKED
    with pytest.raises(ValueError, match="cannot be approved"):
        store.update_action_status(prohibited.id, ActionStatus.APPROVED)


def test_legacy_messages_table_is_migrated(tmp_path: Path) -> None:
    database = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(database)
    connection.execute(
        """
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

    store = SQLiteStore(database)
    message = store.add_message(
        conversation_id="founder-main",
        role="user",
        content="Hello",
        cloud_allowed=False,
    )

    assert message.cloud_allowed is False
    assert store.list_messages("founder-main")[0].cloud_allowed is False


def test_counts_include_context_and_pending_approvals(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    store.upsert_context(
        domain=Scope.COMPANY,
        key="company_name",
        value="EcoFixer",
        visibility=Visibility.COMPANY,
    )
    store.create_action_request(
        title="Merge PR",
        description="Merge PR",
        risk_level=RiskLevel.APPROVAL_REQUIRED,
    )

    counts = store.counts()

    assert counts["contexts"] == 1
    assert counts["pending_approvals"] == 1
