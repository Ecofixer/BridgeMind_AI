from founder_company_ai.models import MemoryCategory, RiskLevel, Scope, Visibility
from founder_company_ai.router import CommandRouter


def test_routes_founder_policy_memory() -> None:
    intent = CommandRouter().route("記住：只有我可以看到私人記憶，員工不能存取")

    assert intent.name == "remember"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["category"] is MemoryCategory.POLICY
    assert intent.payload["visibility"] is Visibility.FOUNDER_ONLY
    assert intent.risk_level is RiskLevel.REVERSIBLE


def test_routes_project_task() -> None:
    intent = CommandRouter().route("新增待辦：完成 EcoFixer iOS 權限測試")

    assert intent.name == "create_task"
    assert intent.payload["scope"] is Scope.PROJECT
    assert intent.payload["project"] == "EcoFixer"


def test_routes_daily_briefing() -> None:
    intent = CommandRouter().route("今天公司有什麼事情？")

    assert intent.name == "daily_briefing"
    assert intent.risk_level is RiskLevel.READ_ONLY


def test_falls_back_to_chat() -> None:
    intent = CommandRouter().route("幫我分析這個產品方向")

    assert intent.name == "chat"
    assert intent.payload["message"] == "幫我分析這個產品方向"
