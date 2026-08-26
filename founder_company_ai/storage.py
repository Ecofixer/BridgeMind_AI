"""SQLite persistence for local founder and company data."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from founder_company_ai.models import (
    ActivityRecord,
    MemoryCategory,
    MemoryRecord,
    MessageRecord,
    RiskLevel,
    Scope,
    TaskRecord,
    TaskStatus,
    Visibility,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SQLiteStore:
    """Small local store with explicit scopes, visibility, and audit records."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    scope TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    visibility TEXT NOT NULL,
                    project TEXT,
                    created_at TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    project TEXT,
                    priority INTEGER NOT NULL DEFAULT 2,
                    approval_required INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, created_at);
                CREATE TABLE IF NOT EXISTS activity (
                    id TEXT PRIMARY KEY,
                    action_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                """
            )

    def add_memory(
        self,
        *,
        content: str,
        scope: Scope,
        category: MemoryCategory,
        visibility: Visibility,
        project: str | None = None,
    ) -> MemoryRecord:
        normalized = content.strip()
        if not normalized:
            raise ValueError("Memory content cannot be empty.")
        record = MemoryRecord(
            id=str(uuid.uuid4()),
            scope=scope,
            category=category,
            content=normalized,
            visibility=visibility,
            project=project.strip() if project and project.strip() else None,
            created_at=utc_now(),
            active=True,
        )
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO memories
                (id, scope, category, content, visibility, project, created_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.id,
                    record.scope.value,
                    record.category.value,
                    record.content,
                    record.visibility.value,
                    record.project,
                    record.created_at,
                    1,
                ),
            )
        return record

    def list_memories(
        self,
        *,
        limit: int = 100,
        scope: Scope | None = None,
        active_only: bool = True,
    ) -> list[MemoryRecord]:
        clauses: list[str] = []
        parameters: list[object] = []
        if scope is not None:
            clauses.append("scope = ?")
            parameters.append(scope.value)
        if active_only:
            clauses.append("active = 1")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        parameters.append(max(1, limit))
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id, scope, category, content, visibility, project, created_at, active
                FROM memories {where} ORDER BY created_at DESC LIMIT ?""",
                parameters,
            ).fetchall()
        return [
            MemoryRecord(
                id=row["id"],
                scope=Scope(row["scope"]),
                category=MemoryCategory(row["category"]),
                content=row["content"],
                visibility=Visibility(row["visibility"]),
                project=row["project"],
                created_at=row["created_at"],
                active=bool(row["active"]),
            )
            for row in rows
        ]

    def add_task(
        self,
        *,
        title: str,
        scope: Scope,
        project: str | None = None,
        priority: int = 2,
        approval_required: bool = False,
    ) -> TaskRecord:
        normalized = title.strip()
        if not normalized:
            raise ValueError("Task title cannot be empty.")
        if priority not in {1, 2, 3}:
            raise ValueError("Priority must be 1, 2, or 3.")
        timestamp = utc_now()
        record = TaskRecord(
            id=str(uuid.uuid4()),
            title=normalized,
            status=TaskStatus.OPEN,
            scope=scope,
            project=project.strip() if project and project.strip() else None,
            priority=priority,
            approval_required=approval_required,
            created_at=timestamp,
            updated_at=timestamp,
        )
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO tasks
                (id, title, status, scope, project, priority, approval_required, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.id,
                    record.title,
                    record.status.value,
                    record.scope.value,
                    record.project,
                    record.priority,
                    int(record.approval_required),
                    record.created_at,
                    record.updated_at,
                ),
            )
        return record

    def list_tasks(self, *, status: TaskStatus | None = None, limit: int = 100) -> list[TaskRecord]:
        parameters: list[object] = []
        where = ""
        if status is not None:
            where = "WHERE status = ?"
            parameters.append(status.value)
        parameters.append(max(1, limit))
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id, title, status, scope, project, priority, approval_required,
                created_at, updated_at FROM tasks {where}
                ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1
                WHEN 'blocked' THEN 2 ELSE 3 END, priority ASC, created_at DESC LIMIT ?""",
                parameters,
            ).fetchall()
        return [
            TaskRecord(
                id=row["id"],
                title=row["title"],
                status=TaskStatus(row["status"]),
                scope=Scope(row["scope"]),
                project=row["project"],
                priority=int(row["priority"]),
                approval_required=bool(row["approval_required"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (status.value, utc_now(), task_id),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Unknown task: {task_id}")

    def add_message(self, *, conversation_id: str, role: str, content: str) -> MessageRecord:
        if role not in {"user", "assistant"}:
            raise ValueError("Role must be 'user' or 'assistant'.")
        normalized = content.strip()
        if not normalized:
            raise ValueError("Message content cannot be empty.")
        record = MessageRecord(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=normalized,
            created_at=utc_now(),
        )
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (record.id, record.conversation_id, record.role, record.content, record.created_at),
            )
        return record

    def list_messages(self, conversation_id: str, *, limit: int = 50) -> list[MessageRecord]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT id, conversation_id, role, content, created_at FROM (
                SELECT id, conversation_id, role, content, created_at FROM messages
                WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?)
                ORDER BY created_at ASC""",
                (conversation_id, max(1, limit)),
            ).fetchall()
        return [
            MessageRecord(
                id=row["id"],
                conversation_id=row["conversation_id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def log_activity(
        self,
        *,
        action_type: str,
        summary: str,
        risk_level: RiskLevel,
        status: str = "completed",
        details: dict[str, object] | None = None,
    ) -> ActivityRecord:
        record = ActivityRecord(
            id=str(uuid.uuid4()),
            action_type=action_type,
            summary=summary.strip(),
            risk_level=risk_level,
            status=status,
            details=details or {},
            created_at=utc_now(),
        )
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO activity
                (id, action_type, summary, risk_level, status, details_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.id,
                    record.action_type,
                    record.summary,
                    record.risk_level.value,
                    record.status,
                    json.dumps(record.details, ensure_ascii=False, sort_keys=True),
                    record.created_at,
                ),
            )
        return record

    def list_activity(self, *, limit: int = 100) -> list[ActivityRecord]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT id, action_type, summary, risk_level, status, details_json, created_at
                FROM activity ORDER BY created_at DESC LIMIT ?""",
                (max(1, limit),),
            ).fetchall()
        return [
            ActivityRecord(
                id=row["id"],
                action_type=row["action_type"],
                summary=row["summary"],
                risk_level=RiskLevel(row["risk_level"]),
                status=row["status"],
                details=json.loads(row["details_json"] or "{}"),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def counts(self) -> dict[str, int]:
        with self._connection() as connection:
            memories = connection.execute("SELECT COUNT(*) FROM memories WHERE active = 1").fetchone()[0]
            open_tasks = connection.execute("SELECT COUNT(*) FROM tasks WHERE status != 'done'").fetchone()[0]
            activities = connection.execute("SELECT COUNT(*) FROM activity").fetchone()[0]
        return {"memories": int(memories), "open_tasks": int(open_tasks), "activities": int(activities)}
