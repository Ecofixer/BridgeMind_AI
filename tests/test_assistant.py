from pathlib import Path

from founder_company_ai.assistant import FounderCompanyAssistant
from founder_company_ai.models import MemoryCategory
from founder_company_ai.router import CommandRouter
from founder_company_ai.services.actions import ActionService
from founder_company_ai.storage import SQLiteStore


def build_assistant(tmp_path: Path) -> tuple[FounderCompanyAssistant, SQLiteStore]:
    store = SQLiteStore(tmp_path / "assistant.sqlite3")
    assistant = FounderCompanyAssistant(
        store=store,
        router=CommandRouter(),
        actions=ActionService(store),
        provider=None,
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
        message="幫我分析產品方向", conversation_id="founder-main"
    )

    assert "本機安全模式" in reply
    assert "OPENAI_API_KEY" in reply
