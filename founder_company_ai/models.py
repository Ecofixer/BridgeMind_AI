"""Typed domain models for context, memory, tasks, messages, and actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Scope(str, Enum):
    FOUNDER = "founder"
    COMPANY = "company"
    PROJECT = "project"


class Visibility(str, Enum):
    FOUNDER_ONLY = "founder_only"
    COMPANY = "company"
    PROJECT = "project"


class MemoryCategory(str, Enum):
    PREFERENCE = "preference"
    DECISION = "decision"
    POLICY = "policy"
    FACT = "fact"
    NOTE = "note"


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class RiskLevel(str, Enum):
    READ_ONLY = "read_only"
    DRAFT = "draft"
    REVERSIBLE = "reversible"
    APPROVAL_REQUIRED = "approval_required"
    PROHIBITED = "prohibited"


class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ContextRecord:
    id: str
    domain: Scope
    key: str
    value: str
    visibility: Visibility
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    id: str
    scope: Scope
    category: MemoryCategory
    content: str
    visibility: Visibility
    project: str | None
    created_at: str
    active: bool = True


@dataclass(frozen=True, slots=True)
class TaskRecord:
    id: str
    title: str
    status: TaskStatus
    scope: Scope
    project: str | None
    priority: int
    approval_required: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class MessageRecord:
    id: str
    conversation_id: str
    role: str
    content: str
    cloud_allowed: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class ActionRequestRecord:
    id: str
    title: str
    description: str
    risk_level: RiskLevel
    status: ActionStatus
    payload: dict[str, Any]
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ActivityRecord:
    id: str
    action_type: str
    summary: str
    risk_level: RiskLevel
    status: str
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass(frozen=True, slots=True)
class Intent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    risk_level: RiskLevel = RiskLevel.READ_ONLY
