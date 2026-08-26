"""SQLite persistence with founder privacy, approvals, and auditability."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from founder_company_ai.models import (
    ActionRequestRecord,
    ActionStatus,
    ActivityRecord,
    ContextRecord,
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
    """Local V1 system of record; authorization invariants live here, not only in UI."""

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
                CREATE TABLE IF NOT EXISTS context_entries (
                    id TEXT PRIMARY KEY, domain TEXT NOT NULL, key TEXT NOT NULL,
                    value TEXT NOT NULL, visibility TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(domain, key)
                );
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY, scope TEXT NOT NULL, category TEXT NOT NULL,
                    content TEXT NOT NULL, visibility TEXT NOT NULL, project TEXT,
                    created_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL,
                    scope TEXT NOT NULL, project TEXT, priority INTEGER NOT NULL DEFAULT 2,
                    approval_required INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT NOT NULL, cloud_allowed INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages(conversation_id, created_at);
                CREATE TABLE IF NOT EXISTS action_requests (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
                    risk_level TEXT NOT NULL, status TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS activity (
                    id TEXT PRIMARY KEY, action_type TEXT NOT NULL, summary TEXT NOT NULL,
                    risk_level TEXT NOT NULL, status TEXT NOT NULL,
                    details_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
                );
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(messages)")}
            if "cloud_allowed" not in columns:
                connection.execute(
                    "ALTER TABLE messages ADD COLUMN cloud_allowed INTEGER NOT NULL DEFAULT 1"
                )

    @staticmethod
    def _private_invariant(scope: Scope, visibility: Visibility) -> None:
        if scope is Scope.FOUNDER and visibility is not Visibility.FOUNDER_ONLY:
            raise ValueError("Founder data must remain founder-only.")

    def upsert_context(
        self, *, domain: Scope, key: str, value: str, visibility: Visibility
    ) -> ContextRecord:
        key, value = key.strip(), value.strip()
        if not key or not value:
            raise ValueError("Context key and value cannot be empty.")
        self._private_invariant(domain, visibility)
        now = utc_now()
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT id, created_at FROM context_entries WHERE domain=? AND key=?",
                (domain.value, key),
            ).fetchone()
            record_id = existing["id"] if existing else str(uuid.uuid4())
            created_at = existing["created_at"] if existing else now
            connection.execute(
                """INSERT INTO context_entries
                   (id,domain,key,value,visibility,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?)
                   ON CONFLICT(domain,key) DO UPDATE SET
                     value=excluded.value, visibility=excluded.visibility,
                     updated_at=excluded.updated_at""",
                (record_id, domain.value, key, value, visibility.value, created_at, now),
            )
        return ContextRecord(record_id, domain, key, value, visibility, created_at, now)

    def list_context(
        self, *, domain: Scope | None = None, limit: int = 100
    ) -> list[ContextRecord]:
        where, parameters = ("WHERE domain=?", [domain.value]) if domain else ("", [])
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id,domain,key,value,visibility,created_at,updated_at
                    FROM context_entries {where} ORDER BY domain,key LIMIT ?""",
                [*parameters, max(1, limit)],
            ).fetchall()
        return [
            ContextRecord(
                row["id"], Scope(row["domain"]), row["key"], row["value"],
                Visibility(row["visibility"]), row["created_at"], row["updated_at"]
            )
            for row in rows
        ]

    def add_memory(
        self, *, content: str, scope: Scope, category: MemoryCategory,
        visibility: Visibility, project: str | None = None
    ) -> MemoryRecord:
        content = content.strip()
        if not content:
            raise ValueError("Memory content cannot be empty.")
        self._private_invariant(scope, visibility)
        record = MemoryRecord(
            str(uuid.uuid4()), scope, category, content, visibility,
            project.strip() if project and project.strip() else None, utc_now(), True
        )
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO memories VALUES (?,?,?,?,?,?,?,?)",
                (record.id, scope.value, category.value, content, visibility.value,
                 record.project, record.created_at, 1),
            )
        return record

    def list_memories(
        self, *, limit: int = 100, scope: Scope | None = None, active_only: bool = True
    ) -> list[MemoryRecord]:
        clauses, parameters = [], []
        if scope:
            clauses.append("scope=?")
            parameters.append(scope.value)
        if active_only:
            clauses.append("active=1")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id,scope,category,content,visibility,project,created_at,active
                    FROM memories {where} ORDER BY created_at DESC LIMIT ?""",
                [*parameters, max(1, limit)],
            ).fetchall()
        return [
            MemoryRecord(
                row["id"], Scope(row["scope"]), MemoryCategory(row["category"]),
                row["content"], Visibility(row["visibility"]), row["project"],
                row["created_at"], bool(row["active"])
            )
            for row in rows
        ]

    def deactivate_memory(self, memory_id: str) -> None:
        with self._connection() as connection:
            result = connection.execute("UPDATE memories SET active=0 WHERE id=?", (memory_id,))
            if result.rowcount == 0:
                raise KeyError(f"Unknown memory: {memory_id}")

    def add_task(
        self, *, title: str, scope: Scope, project: str | None = None,
        priority: int = 2, approval_required: bool = False
    ) -> TaskRecord:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")
        if priority not in {1, 2, 3}:
            raise ValueError("Priority must be 1, 2, or 3.")
        now = utc_now()
        record = TaskRecord(
            str(uuid.uuid4()), title, TaskStatus.OPEN, scope,
            project.strip() if project and project.strip() else None,
            priority, approval_required, now, now
        )
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)",
                (record.id, title, record.status.value, scope.value, record.project,
                 priority, int(approval_required), now, now),
            )
        return record

    def list_tasks(
        self, *, status: TaskStatus | None = None, limit: int = 100
    ) -> list[TaskRecord]:
        where, parameters = ("WHERE status=?", [status.value]) if status else ("", [])
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id,title,status,scope,project,priority,approval_required,
                           created_at,updated_at FROM tasks {where}
                    ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1
                              WHEN 'blocked' THEN 2 ELSE 3 END,
                             priority, created_at DESC LIMIT ?""",
                [*parameters, max(1, limit)],
            ).fetchall()
        return [
            TaskRecord(
                row["id"], row["title"], TaskStatus(row["status"]), Scope(row["scope"]),
                row["project"], int(row["priority"]), bool(row["approval_required"]),
                row["created_at"], row["updated_at"]
            )
            for row in rows
        ]

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        with self._connection() as connection:
            result = connection.execute(
                "UPDATE tasks SET status=?,updated_at=? WHERE id=?",
                (status.value, utc_now(), task_id),
            )
            if result.rowcount == 0:
                raise KeyError(f"Unknown task: {task_id}")

    def add_message(
        self, *, conversation_id: str, role: str, content: str, cloud_allowed: bool = True
    ) -> MessageRecord:
        if role not in {"user", "assistant"}:
            raise ValueError("Role must be 'user' or 'assistant'.")
        content = content.strip()
        if not content:
            raise ValueError("Message content cannot be empty.")
        record = MessageRecord(
            str(uuid.uuid4()), conversation_id, role, content, cloud_allowed, utc_now()
        )
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO messages
                   (id,conversation_id,role,content,cloud_allowed,created_at)
                   VALUES (?,?,?,?,?,?)""",
                (record.id, conversation_id, role, content, int(cloud_allowed), record.created_at),
            )
        return record

    def list_messages(
        self, conversation_id: str, *, limit: int = 50, cloud_allowed_only: bool = False
    ) -> list[MessageRecord]:
        cloud_clause = "AND cloud_allowed=1" if cloud_allowed_only else ""
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id,conversation_id,role,content,cloud_allowed,created_at FROM (
                    SELECT id,conversation_id,role,content,cloud_allowed,created_at
                    FROM messages WHERE conversation_id=? {cloud_clause}
                    ORDER BY created_at DESC LIMIT ?)
                    ORDER BY created_at""",
                (conversation_id, max(1, limit)),
            ).fetchall()
        return [
            MessageRecord(
                row["id"], row["conversation_id"], row["role"], row["content"],
                bool(row["cloud_allowed"]), row["created_at"]
            )
            for row in rows
        ]

    def create_action_request(
        self, *, title: str, description: str, risk_level: RiskLevel,
        payload: dict[str, object] | None = None
    ) -> ActionRequestRecord:
        title = title.strip()
        if not title:
            raise ValueError("Action title cannot be empty.")
        now = utc_now()
        status = ActionStatus.BLOCKED if risk_level is RiskLevel.PROHIBITED else ActionStatus.PENDING
        record = ActionRequestRecord(
            str(uuid.uuid4()), title, description.strip(), risk_level, status,
            dict(payload or {}), now, now
        )
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO action_requests VALUES (?,?,?,?,?,?,?,?)",
                (record.id, title, record.description, risk_level.value, status.value,
                 json.dumps(record.payload, ensure_ascii=False, sort_keys=True), now, now),
            )
        return record

    def list_action_requests(
        self, *, status: ActionStatus | None = None, limit: int = 100
    ) -> list[ActionRequestRecord]:
        where, parameters = ("WHERE status=?", [status.value]) if status else ("", [])
        with self._connection() as connection:
            rows = connection.execute(
                f"""SELECT id,title,description,risk_level,status,payload_json,
                           created_at,updated_at FROM action_requests {where}
                    ORDER BY created_at DESC LIMIT ?""",
                [*parameters, max(1, limit)],
            ).fetchall()
        return [
            ActionRequestRecord(
                row["id"], row["title"], row["description"], RiskLevel(row["risk_level"]),
                ActionStatus(row["status"]), json.loads(row["payload_json"] or "{}"),
                row["created_at"], row["updated_at"]
            )
            for row in rows
        ]

    def update_action_status(self, action_id: str, status: ActionStatus) -> None:
        if status not in {ActionStatus.APPROVED, ActionStatus.REJECTED}:
            raise ValueError("V1 only supports approval or rejection.")
        with self._connection() as connection:
            current = connection.execute(
                "SELECT risk_level FROM action_requests WHERE id=?", (action_id,)
            ).fetchone()
            if current is None:
                raise KeyError(f"Unknown action request: {action_id}")
            if current["risk_level"] == RiskLevel.PROHIBITED.value:
                raise ValueError("A prohibited action cannot be approved.")
            connection.execute(
                "UPDATE action_requests SET status=?,updated_at=? WHERE id=?",
                (status.value, utc_now(), action_id),
            )

    def log_activity(
        self, *, action_type: str, summary: str, risk_level: RiskLevel,
        status: str = "completed", details: dict[str, object] | None = None
    ) -> ActivityRecord:
        record = ActivityRecord(
            str(uuid.uuid4()), action_type.strip(), summary.strip(), risk_level,
            status.strip(), dict(details or {}), utc_now()
        )
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO activity VALUES (?,?,?,?,?,?,?)",
                (record.id, record.action_type, record.summary, risk_level.value, record.status,
                 json.dumps(record.details, ensure_ascii=False, sort_keys=True), record.created_at),
            )
        return record

    def list_activity(self, *, limit: int = 100) -> list[ActivityRecord]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT id,action_type,summary,risk_level,status,details_json,created_at
                   FROM activity ORDER BY created_at DESC LIMIT ?""",
                (max(1, limit),),
            ).fetchall()
        return [
            ActivityRecord(
                row["id"], row["action_type"], row["summary"], RiskLevel(row["risk_level"]),
                row["status"], json.loads(row["details_json"] or "{}"), row["created_at"]
            )
            for row in rows
        ]

    def counts(self) -> dict[str, int]:
        queries = {
            "contexts": "SELECT COUNT(*) FROM context_entries",
            "memories": "SELECT COUNT(*) FROM memories WHERE active=1",
            "open_tasks": "SELECT COUNT(*) FROM tasks WHERE status!='done'",
            "pending_approvals": "SELECT COUNT(*) FROM action_requests WHERE status='pending'",
            "activities": "SELECT COUNT(*) FROM activity",
        }
        with self._connection() as connection:
            return {key: int(connection.execute(sql).fetchone()[0]) for key, sql in queries.items()}
