"""Deterministic routing for safe local commands."""

from __future__ import annotations

import re

from founder_company_ai.models import Intent, MemoryCategory, RiskLevel, Scope, Visibility


PERSONAL_OS_NAME = "Youchen AI OS"
COMPANY_OS_NAME = "EcoFixer AI OS"

REMEMBER_PREFIXES = (
    "請幫我記住", "请帮我记住", "幫我記住", "帮我记住", "請記住", "请记住",
    "記住", "记住", "remember",
)
TASK_PREFIXES = (
    "請新增待辦", "请新增待办", "新增待辦", "新增待办", "建立任務", "建立任务",
    "加入待辦", "加入待办", "提醒我", "add task",
)
PRIVATE_SIGNALS = (
    "只有我", "私人", "私密", "創辦人", "创办人", "我本人", "founder-only",
    "不可公開", "不得公開", "不能公開", "不可以公開", "不可分享", "不得分享",
    "不能分享", "不可以分享", "不可以讓員工", "不能讓員工", "不可讓員工",
    "不可以让员工", "不能让员工", "不可让员工", "do not expose", "do not share",
)
COMPANY_SIGNALS = (
    "公司", "company", "團隊", "团队", "員工", "员工", "營運", "运营",
)


def _clean_after_prefix(text: str, prefixes: tuple[str, ...]) -> str | None:
    stripped = text.strip()
    lowered = stripped.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix.lower()):
            return stripped[len(prefix):].lstrip(" ：:，,。.")
    return None


def _contains_private_signal(content: str) -> bool:
    lowered = content.lower()
    return any(token in lowered for token in PRIVATE_SIGNALS)


def _infer_category(content: str) -> MemoryCategory:
    lowered = content.lower()
    if any(token in lowered for token in (
        "規則", "规则", "必須", "必须", "不得", "不能", "不可以", "不應", "不应",
        "不可", "policy",
    )):
        return MemoryCategory.POLICY
    if any(token in lowered for token in (
        "決定", "决定", "先不", "之後", "之后", "暫緩", "暂停", "decision",
    )):
        return MemoryCategory.DECISION
    if any(token in lowered for token in (
        "偏好", "喜歡", "喜欢", "習慣", "习惯", "prefer",
    )):
        return MemoryCategory.PREFERENCE
    if any(token in lowered for token in ("事實", "事实", "目前", "fact")):
        return MemoryCategory.FACT
    return MemoryCategory.NOTE


def _extract_project(content: str) -> str | None:
    lowered = content.lower()

    if any(token in lowered for token in (
        "ecofixer ai os",
        "ecofixer ai",
        "公司 ai",
        "公司ai",
        "company ai",
    )):
        return COMPANY_OS_NAME

    if any(token in lowered for token in (
        "youchen ai os",
        "youchen ai",
        "founder + company ai",
        "founder company ai",
        "founder ai",
        "ai agent",
        "創辦人 ai",
        "创办人 ai",
    )):
        return PERSONAL_OS_NAME

    if "ecofixer" in lowered or "易修繕" in content or "易修缮" in content:
        return "EcoFixer"

    match = re.search(
        r"(?:專案|项目|project)\s*[:：]?\s*([A-Za-z0-9][A-Za-z0-9 _+\-]{1,50})",
        content,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _infer_scope(
    content: str,
    project: str | None,
    *,
    private_precedence: bool = False,
) -> Scope:
    if private_precedence and _contains_private_signal(content):
        return Scope.FOUNDER
    if project:
        return Scope.PROJECT
    if _contains_private_signal(content):
        return Scope.FOUNDER
    lowered = content.lower()
    if any(token in lowered for token in COMPANY_SIGNALS):
        return Scope.COMPANY
    return Scope.FOUNDER


def _infer_visibility(content: str, scope: Scope) -> Visibility:
    if _contains_private_signal(content):
        return Visibility.FOUNDER_ONLY
    if scope is Scope.PROJECT:
        return Visibility.PROJECT
    if scope is Scope.COMPANY:
        return Visibility.COMPANY
    return Visibility.FOUNDER_ONLY


class CommandRouter:
    """Routes explicit local commands before a cloud model is considered."""

    def route(self, text: str) -> Intent:
        normalized = text.strip()
        if not normalized:
            return Intent(name="empty")

        memory_content = _clean_after_prefix(normalized, REMEMBER_PREFIXES)
        if memory_content is not None:
            if not memory_content:
                return Intent(name="invalid_memory")
            project = _extract_project(memory_content)
            scope = _infer_scope(
                memory_content,
                project,
                private_precedence=True,
            )
            return Intent(
                name="remember",
                payload={
                    "content": memory_content,
                    "scope": scope,
                    "category": _infer_category(memory_content),
                    "visibility": _infer_visibility(memory_content, scope),
                    "project": project,
                },
                risk_level=RiskLevel.REVERSIBLE,
            )

        task_content = _clean_after_prefix(normalized, TASK_PREFIXES)
        if task_content is not None:
            if not task_content:
                return Intent(name="invalid_task")
            project = _extract_project(task_content)
            return Intent(
                name="create_task",
                payload={
                    "title": task_content,
                    "scope": _infer_scope(task_content, project),
                    "project": project,
                },
                risk_level=RiskLevel.REVERSIBLE,
            )

        lowered = normalized.lower()
        if any(phrase in lowered for phrase in (
            "今天公司有什麼", "今天公司有什么", "今天有什麼重要", "今天有什么重要",
            "daily briefing", "company briefing",
        )):
            return Intent(
                name="daily_briefing",
                confidence=0.98,
                risk_level=RiskLevel.READ_ONLY,
            )

        if any(phrase in lowered for phrase in (
            "列出記憶", "列出记忆", "查看記憶", "查看记忆", "show memories", "list memories",
        )):
            return Intent(
                name="list_memories",
                confidence=0.98,
                risk_level=RiskLevel.READ_ONLY,
            )

        if any(phrase in lowered for phrase in (
            "列出待辦", "列出待办", "查看待辦", "查看待办", "show tasks", "list tasks",
        )):
            return Intent(
                name="list_tasks",
                confidence=0.98,
                risk_level=RiskLevel.READ_ONLY,
            )

        return Intent(
            name="chat",
            payload={"message": normalized},
            confidence=0.7,
            risk_level=RiskLevel.READ_ONLY,
        )
