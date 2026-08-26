from pathlib import Path

from founder_company_ai.models import (
    MemoryCategory,
    RiskLevel,
    Scope,
    TaskStatus,
    Visibility,
)
from founder_company_ai.storage import SQLiteStore


def test_store_persists_memory_task_message_and_activity(tmp_path: Path) -> None:
    database = tmp_path / "assistant.sqlite3"
    store = SQLiteStore(database)

    memory = store.add_memory(
        content="金額與比例必須可設定",
        scope=Scope.PROJECT,
        category=MemoryCategory.DECISION,
        visibility=Visibility.PROJECT,
        project="EcoFixer",
    )
    task = store.add_task(title="完成權限模型", scope=Scope.COMPANY, priority=1)
    store.add_message(
        conversation_id="founder-main", role="user", content="今天要做什麼？"
    )
    store.log_activity(
        action_type="test", summary="Test audit event", risk_level=RiskLevel.READ_ONLY
    )

    reopened = SQLiteStore(database)
    memories = reopened.list_memories()
    tasks = reopened.list_tasks()
    messages = reopened.list_messages("founder-main")
    activity = reopened.list_activity()

    assert memories[0].id == memory.id
    assert memories[0].project == "EcoFixer"
    assert tasks[0].id == task.id
    assert tasks[0].status is TaskStatus.OPEN
    assert messages[0].content == "今天要做什麼？"
    assert activity[0].action_type == "test"


def test_updates_task_status(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    task = store.add_task(title="Review", scope=Scope.FOUNDER)
    store.update_task_status(task.id, TaskStatus.DONE)
    assert store.list_tasks()[0].status is TaskStatus.DONE
