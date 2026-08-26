"""Safe local action execution."""

from __future__ import annotations

from founder_company_ai.models import Intent, RiskLevel, TaskStatus
from founder_company_ai.storage import SQLiteStore


class ActionService:
    """Executes only reversible local V1 actions."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def execute(self, intent: Intent) -> str:
        if intent.name == "remember":
            record = self.store.add_memory(**intent.payload)
            self.store.log_activity(
                action_type="memory.created",
                summary=f"Stored {record.category.value} in {record.scope.value} memory.",
                risk_level=RiskLevel.REVERSIBLE,
                details={
                    "memory_id": record.id,
                    "scope": record.scope.value,
                    "visibility": record.visibility.value,
                    "project": record.project,
                },
            )
            visibility_label = {
                "founder_only": "只有創辦人可見",
                "company": "公司範圍",
                "project": "專案範圍",
            }[record.visibility.value]
            project_text = f"；專案：{record.project}" if record.project else ""
            return (
                f"已記錄為「{record.category.value}」記憶，"
                f"範圍是 {record.scope.value}，{visibility_label}{project_text}。"
            )

        if intent.name == "create_task":
            record = self.store.add_task(**intent.payload)
            self.store.log_activity(
                action_type="task.created",
                summary=f"Created task: {record.title}",
                risk_level=RiskLevel.REVERSIBLE,
                details={"task_id": record.id, "scope": record.scope.value},
            )
            project_text = f"（{record.project}）" if record.project else ""
            return f"已建立待辦{project_text}：{record.title}"

        if intent.name == "daily_briefing":
            open_tasks = [
                task for task in self.store.list_tasks(limit=20)
                if task.status is not TaskStatus.DONE
            ]
            recent_memories = self.store.list_memories(limit=5)
            self.store.log_activity(
                action_type="briefing.generated",
                summary="Generated founder daily briefing.",
                risk_level=RiskLevel.READ_ONLY,
                details={
                    "open_task_count": len(open_tasks),
                    "memory_count": len(recent_memories),
                },
            )
            if not open_tasks and not recent_memories:
                return (
                    "目前沒有已記錄的待辦或近期決策。"
                    "你可以說「新增待辦：……」或「記住：……」開始建立公司脈絡。"
                )
            lines = ["### 今日 Founder Briefing"]
            if open_tasks:
                lines.append(f"\n**未完成事項：{len(open_tasks)} 項**")
                for task in open_tasks[:8]:
                    project = f" · {task.project}" if task.project else ""
                    lines.append(f"- P{task.priority} · {task.title}{project}")
            if recent_memories:
                lines.append("\n**近期記憶／決策**")
                for memory in recent_memories[:5]:
                    project = f" · {memory.project}" if memory.project else ""
                    lines.append(f"- {memory.category.value} · {memory.content}{project}")
            return "\n".join(lines)

        if intent.name == "list_memories":
            memories = self.store.list_memories(limit=20)
            self.store.log_activity(
                action_type="memory.listed",
                summary="Listed active memories.",
                risk_level=RiskLevel.READ_ONLY,
                details={"count": len(memories)},
            )
            if not memories:
                return "目前尚未建立記憶。"
            lines = ["### 已啟用記憶"]
            for memory in memories:
                project = f" · {memory.project}" if memory.project else ""
                lines.append(
                    f"- **{memory.scope.value}/{memory.category.value}** · "
                    f"{memory.content}{project}"
                )
            return "\n".join(lines)

        if intent.name == "invalid_memory":
            return "要記住的內容是空的。請說「記住：你的決策或規則」。"
        if intent.name == "invalid_task":
            return "待辦內容是空的。請說「新增待辦：要完成的事情」。"
        if intent.name == "empty":
            return "請輸入一個問題或任務。"
        raise ValueError(f"Unsupported local intent: {intent.name}")
