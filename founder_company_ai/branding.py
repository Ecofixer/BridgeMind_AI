"""Canonical product names and voice identity."""

PERSONAL_OS_NAME = "Youchen AI OS"
COMPANY_OS_NAME = "EcoFixer AI OS"
WAKE_PHRASE = "Hey Youchen"
INTERNAL_CORE_NAME = "Founder + Company AI Core"


def workspace_label(scope: str) -> str:
    """Return the user-facing workspace name for a stored scope."""
    return COMPANY_OS_NAME if scope in {"company", "project"} else PERSONAL_OS_NAME
