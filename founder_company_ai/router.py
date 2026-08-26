"""Deterministic routing for safe local commands."""

from __future__ import annotations

import re

from founder_company_ai.models import Intent, MemoryCategory, RiskLevel, Scope, Visibility


REMEMBER_PREFIXES = (
    "請幫我記住", "请帮我记住", "幫我記住", "帮我记住", "請記住", "请记住",
    "記住", "记住", "remember",
)
TASK_PREFIXES = (
    "請新增待辦", "请新增待办", "新增待辦", "新增待办", "建立任務", "建立任务",
    "加入待辦", "加入待办", "提醒我", "add task",
)


def _clean_after_prefix(text: str, prefixes: tuple[str, ...]) -> str | None:
    lowered = text.strip().lower()
    for prefix in prefixes:
        if lowered.startswith(prefix.lower()):
            return text.strip()[len(prefix):].lstrip(" ：:，,。.")
    return None


def _infer_category(content: str) -> MemoryCategory:
    lowered = content.lower()
    if any(token in lowered for token in (
        "規則", "规则", "必須", "必须", "不得", "不能", "不可以", "不應", "不应", "policy"
    )):
        return MemoryCategory.POLICY
    if any(token in lowered for token in ("決定", "决定", "先不", "之後", "之后", "decision")):
        return MemoryCategory.DECISION
    if any(token in lowered for token in ("偏好", "喜歡", "喜欢", "習慣", "习惯", "prefer")):
        return MemoryCategory.PREFERENCE
    if any(token in lowered for token in ("事實", "事实", "目前", "is ", "fact")):
        return MemoryCategory.FACT
    return MemoryCategory.NOTE


def _extract_project(content: str) -> str | None:
    if "ecofixer" in content.lower():
        return "EcoFixer"
    match = re.search(
        r"(?:專案|项目|project)\s*[:：]?\s*([A-Za-z0-9][A-Za-z0-9_-]{1,50})",
        content,
        flags=re.IGNORECASE,
    )
    return match.group(1) if match else None


def _infer_scope(content: str, project: str | None) -> Scope:
    if project:
        return Scope.PROJECT
    lowered = content.lower()
    if any(token in lowered for token in (
        "只有我", "私人", "私密", "創辦人", "创办人", "founder-only"
    )):
        return Scope.FOUNDER
    if any(token in lowered for token in ("公司", "company", "團隊", "团队", "員工", "员工")):
        return Scope.COMPANY
    return Scope.FOUNDER


def _infer_visibility(content: str, scope: Scope) -> Visibility:
    lowered = content.lower()
    if any(token in lowered for token in (
        "私人", "私密", "只有我", "創辦人", "创办人", "founder-only"
    )):
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
            scope = _infer_scope(memory_content, project)
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
            return Intent(name="daily_briefing", confidence=0.98)

        if any(phrase in lowered for phrase in (
            "列出記憶", "列出记忆", "查看記憶", "查看记忆", "show memories", "list memories",
        )):
            return Intent(name="list_memories", confidence=0.98)

        return Intent(name="chat", payload={"message": normalized}, confidence=0.7)
