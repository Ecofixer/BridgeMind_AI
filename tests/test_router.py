from founder_company_ai.branding import COMPANY_OS_NAME, PERSONAL_OS_NAME
from founder_company_ai.models import MemoryCategory, RiskLevel, Scope, Visibility
from founder_company_ai.router import CommandRouter, infer_action_risk


def test_routes_wake_phrase_acknowledgement() -> None:
    intent = CommandRouter().route("Hey Youchen")

    assert intent.name == "wake_acknowledgement"
    assert intent.risk_level is RiskLevel.READ_ONLY


def test_routes_wake_phrase_followed_by_command() -> None:
    intent = CommandRouter().route("Hey Youchen，新增待辦：完成權限測試")

    assert intent.name == "create_task"
    assert intent.payload["title"] == "完成權限測試"


def test_routes_founder_private_policy() -> None:
    intent = CommandRouter().route("記住：只有我可以看到私人記憶，員工不能存取")

    assert intent.name == "remember"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["category"] is MemoryCategory.POLICY
    assert intent.payload["visibility"] is Visibility.FOUNDER_ONLY
    assert intent.risk_level is RiskLevel.REVERSIBLE


def test_private_company_ai_policy_stays_founder_only() -> None:
    intent = CommandRouter().route("記住：公司 AI 不可以讓員工看到我的長期記憶")

    assert intent.name == "remember"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["visibility"] is Visibility.FOUNDER_ONLY
    assert intent.payload["project"] == PERSONAL_OS_NAME


def test_routes_ecofixer_task_to_company_os_project() -> None:
    intent = CommandRouter().route("新增待辦：完成 EcoFixer iOS 權限測試")

    assert intent.name == "create_task"
    assert intent.payload["scope"] is Scope.PROJECT
    assert intent.payload["project"] == COMPANY_OS_NAME


def test_routes_founder_ai_task_to_personal_os() -> None:
    intent = CommandRouter().route("新增待辦：完成 AI Agent 語音權限測試")

    assert intent.name == "create_task"
    assert intent.payload["scope"] is Scope.FOUNDER
    assert intent.payload["project"] == PERSONAL_OS_NAME


def test_routes_action_proposal_and_risk() -> None:
    intent = CommandRouter().route("建立提案：Merge 修正完成的 PR")

    assert intent.name == "create_action_request"
    assert intent.risk_level is RiskLevel.APPROVAL_REQUIRED
    assert intent.payload["risk_level"] is RiskLevel.APPROVAL_REQUIRED


def test_classifies_prohibited_reversible_and_draft_actions() -> None:
    assert infer_action_risk("刪除正式資料庫") is RiskLevel.PROHIBITED
    assert infer_action_risk("建立 branch") is RiskLevel.REVERSIBLE
    assert infer_action_risk("整理產品方案") is RiskLevel.DRAFT


def test_routes_daily_briefing_and_lists() -> None:
    router = CommandRouter()

    assert router.route("今天公司有什麼事情？").name == "daily_briefing"
    assert router.route("列出記憶").name == "list_memories"
    assert router.route("列出待辦").name == "list_tasks"


def test_falls_back_to_chat() -> None:
    intent = CommandRouter().route("幫我分析這個產品方向")

    assert intent.name == "chat"
    assert intent.payload["message"] == "幫我分析這個產品方向"
