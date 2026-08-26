from pathlib import Path
from typing import Sequence

from founder_company_ai.assistant import FounderCompanyAssistant
from founder_company_ai.branding import COMPANY_OS_NAME, PERSONAL_OS_NAME
from founder_company_ai.models import MessageRecord, Scope, Visibility
from founder_company_ai.router import CommandRouter
from founder_company_ai.services.actions import ActionService
from founder_company_ai.storage import SQLiteStore


class RecordingProvider:
    def __init__(self) -> None:
        self.messages: list[MessageRecord] = []
        self.system_prompt = ""

    def reply(self, *, system_prompt: str, messages: Sequence[MessageRecord]) -> str:
        self.system_prompt = system_prompt
        self.messages = list(messages)
        return "分析完成。"

    def transcribe(self, *, audio_bytes: bytes, filename: str = "voice.wav") -> str:
        return "語音內容"


def build_assistant(
    tmp_path: Path,
    *,
    provider: RecordingProvider | None = None,
    allow_cloud_memory_context: bool = False,
) -> tuple[FounderCompanyAssistant, SQLiteStore]:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    assistant = FounderCompanyAssistant(
        store=store,
        router=CommandRouter(),
        actions=ActionService(store),
        provider=provider,
        allow_cloud_memory_context=allow_cloud_memory_context,
    )
    return assistant, store


def test_wake_acknowledgement_uses_product_identity(tmp_path: Path) -> None:
    assistant, _ = build_assistant(tmp_path)

    reply = assistant.handle(message="Hey Youchen", conversation_id="founder-main")

    assert PERSONAL_OS_NAME in reply
    assert COMPANY_OS_NAME in reply


def test_local_memory_command_is_executed_and_not_cloud_eligible(tmp_path: Path) -> None:
    assistant, store = build_assistant(tmp_path)

    reply = assistant.handle(
        message="記住：公司 AI 不可以公開創辦人的私人記憶",
        conversation_id="founder-main",
    )

    assert "已記錄" in reply
    assert len(store.list_messages("founder-main")) == 2
    assert store.list_messages("founder-main", cloud_allowed_only=True) == []


def test_safe_mode_explains_provider_requirement(tmp_path: Path) -> None:
    assistant, _ = build_assistant(tmp_path)

    reply = assistant.handle(
        message="幫我分析產品方向",
        conversation_id="founder-main",
    )

    assert PERSONAL_OS_NAME in reply
    assert "OPENAI_API_KEY" in reply


def test_cloud_chat_excludes_previous_local_commands(tmp_path: Path) -> None:
    provider = RecordingProvider()
    assistant, _ = build_assistant(tmp_path, provider=provider)
    assistant.handle(
        message="記住：這是創辦人私人規則",
        conversation_id="founder-main",
    )

    reply = assistant.handle(
        message="幫我分析產品方向",
        conversation_id="founder-main",
    )

    assert reply == "分析完成。"
    assert [message.content for message in provider.messages] == ["幫我分析產品方向"]
    assert "structured profile" in provider.system_prompt


def test_opt_in_cloud_context_includes_profile(tmp_path: Path) -> None:
    provider = RecordingProvider()
    assistant, store = build_assistant(
        tmp_path,
        provider=provider,
        allow_cloud_memory_context=True,
    )
    store.upsert_context(
        domain=Scope.COMPANY,
        key="company_name",
        value="EcoFixer",
        visibility=Visibility.COMPANY,
    )

    assistant.handle(
        message="幫我分析公司方向",
        conversation_id="founder-main",
    )

    assert "company_name: EcoFixer" in provider.system_prompt


def test_daily_briefing_includes_tasks_and_approvals(tmp_path: Path) -> None:
    assistant, _ = build_assistant(tmp_path)
    assistant.handle(
        message="新增待辦：完成 EcoFixer 權限模型",
        conversation_id="founder-main",
    )
    assistant.handle(
        message="建立提案：Merge 修正完成的 PR",
        conversation_id="founder-main",
    )

    briefing = assistant.handle(
        message="今天公司有什麼事情？",
        conversation_id="founder-main",
    )

    assert "未完成事項：1 項" in briefing
    assert "等待批准：1 項" in briefing


def test_prohibited_action_is_blocked(tmp_path: Path) -> None:
    assistant, store = build_assistant(tmp_path)

    reply = assistant.handle(
        message="建立提案：刪除正式資料庫",
        conversation_id="founder-main",
    )

    assert "禁止" in reply
    assert store.list_action_requests()[0].status.value == "blocked"
