from pathlib import Path

from founder_company_ai.assistant import FounderCompanyAssistant
from founder_company_ai.models import MemoryCategory
from founder_company_ai.router import CommandRouter
from founder_company_ai.services.actions import ActionService
from founder_company_ai.storage import SQLiteStore


class FailingProvider:
    def reply(self, *, system_prompt: str, messages: object) -> str:
        raise RuntimeError("secret provider detail")

    def transcribe(self, *, audio_bytes: bytes, filename: str = "voice.wav") -> str:
        raise NotImplementedError


def build_assistant(
    tmp_path: Path,
    *,
    provider: object | None = None,
) -> tuple[FounderCompanyAssistant, SQLiteStore]:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    assistant = FounderCompanyAssistant(
        store=store,
        router=CommandRouter(),
        actions=ActionService(store),
        provider=provider,  # type: ignore[arg-type]
        allow_cloud_memory_context=False,
    )
    return assistant, store


def test_local_memory_command_is_executed(tmp_path: Path) -> None:
    assistant, store = build_assistant(tmp_path)
    reply = assistant.handle(
        message="記住：公司 AI 不可以公開創辦人的私人記憶",
        conversation_id="founder-main",
    )

    memories = store.list_memories()
    assert "已記錄" in reply
    assert memories[0].category is MemoryCategory.POLICY
    assert len(store.list_activity()) == 1
    assert len(store.list_messages("founder-main")) == 2


def test_safe_mode_explains_provider_requirement(tmp_path: Path) -> None:
    assistant, _ = build_assistant(tmp_path)
    reply = assistant.handle(
        message="幫我分析產品方向",
        conversation_id="founder-main",
    )

    assert "本機安全模式" in reply
    assert "OPENAI_API_KEY" in reply


def test_can_list_open_tasks_through_chat(tmp_path: Path) -> None:
    assistant, store = build_assistant(tmp_path)
    assistant.handle(
        message="新增待辦：完成語音權限測試",
        conversation_id="founder-main",
    )

    reply = assistant.handle(
        message="列出待辦",
        conversation_id="founder-main",
    )

    assert "完成語音權限測試" in reply
    assert any(
        activity.action_type == "task.listed"
        for activity in store.list_activity()
    )


def test_provider_failure_is_audited_without_exposing_raw_error(tmp_path: Path) -> None:
    assistant, store = build_assistant(tmp_path, provider=FailingProvider())

    reply = assistant.handle(
        message="幫我分析產品方向",
        conversation_id="founder-main",
    )

    assert "secret provider detail" not in reply
    assert "無法完成請求" in reply
    activity = store.list_activity()[0]
    assert activity.action_type == "chat.failed"
    assert activity.status == "failed"
    assert activity.details["error_type"] == "RuntimeError"
