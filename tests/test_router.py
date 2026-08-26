from founder_company_ai.branding import COMPANY_OS_NAME, PERSONAL_OS_NAME
from founder_company_ai.models import MemoryCategory, RiskLevel, Scope, Visibility
from founder_company_ai.router import CommandRouter


def test_routes_founder_policy_memory() -> None:
    intent = CommandRouter().route("記住：只有我可以看到私人記憶，員工不能存取")

    assert intent.name == "remember"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["category"] is MemoryCategory.POLICY
    assert intent.payload["visibility"] is Visibility.FOUNDER_ONLY
    assert intent.risk_level is RiskLevel.REVERSIBLE


def test_private_company_ai_policy_stays_founder_only() -> None:
    intent = CommandRouter().route(
        "記住：EcoFixer AI OS 不可以讓員工看到我的長期記憶"
    )

    assert intent.name == "remember"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["category"] is MemoryCategory.POLICY
    assert intent.payload["visibility"] is Visibility.FOUNDER_ONLY
    assert intent.payload["project"] == COMPANY_OS_NAME


def test_routes_ecofixer_project_task() -> None:
    intent = CommandRouter().route("新增待辦：完成 EcoFixer iOS 權限測試")

    assert intent.name == "create_task"
    assert intent.payload["scope"] is Scope.PROJECT
    assert intent.payload["project"] == COMPANY_OS_NAME


def test_routes_youchen_ai_os_task_as_founder_scope() -> None:
    intent = CommandRouter().route("新增待辦：完成 Youchen AI OS 語音權限測試")

    assert intent.name == "create_task"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["project"] == PERSONAL_OS_NAME


def test_routes_generic_ai_agent_to_youchen_ai_os() -> None:
    intent = CommandRouter().route("新增待辦：完成 AI Agent 語音權限測試")

    assert intent.name == "create_task"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["project"] == PERSONAL_OS_NAME


def test_wake_phrase_only_routes_to_acknowledgement() -> None:
    intent = CommandRouter().route("Hey Youchen")

    assert intent.name == "wake_acknowledgement"
    assert intent.risk_level is RiskLevel.READ_ONLY


def test_wake_phrase_is_removed_before_routing() -> None:
    intent = CommandRouter().route("Hey Youchen，今天公司有什麼事情？")

    assert intent.name == "daily_briefing"


def test_wake_alias_is_supported() -> None:
    intent = CommandRouter().route("Hey Uchen, 列出待辦")

    assert intent.name == "list_tasks"


def test_routes_daily_briefing() -> None:
    intent = CommandRouter().route("今天公司有什麼事情？")

    assert intent.name == "daily_briefing"
    assert intent.risk_level is RiskLevel.READ_ONLY


def test_routes_list_tasks() -> None:
    intent = CommandRouter().route("列出待辦")

    assert intent.name == "list_tasks"
    assert intent.risk_level is RiskLevel.READ_ONLY


def test_falls_back_to_chat() -> None:
    intent = CommandRouter().route("幫我分析這個產品方向")

    assert intent.name == "chat"
    assert intent.payload["message"] == "幫我分析這個產品方向"
