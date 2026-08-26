"""Safe local action execution."""

from __future__ import annotations

from founder_company_ai.branding import COMPANY_OS_NAME, PERSONAL_OS_NAME, WAKE_PHRASE
from founder_company_ai.models import ActionStatus, Intent, RiskLevel, TaskStatus
from founder_company_ai.storage import SQLiteStore


class ActionService:
    """Executes only local, auditable V1 actions."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def execute(self, intent: Intent) -> str:
        if intent.name == "wake_acknowledgement":
            self.store.log_activity(
                action_type="voice.wake_detected",
                summary=f"Detected local wake phrase: {WAKE_PHRASE}",
                risk_level=RiskLevel.READ_ONLY,
            )
            return (
                f"我在。這裡是 {PERSONAL_OS_NAME}。"
                f"你要處理個人事項，還是進入 {COMPANY_OS_NAME}？"
            )

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

        if intent.name == "create_action_request":
            record = self.store.create_action_request(**intent.payload)
            self.store.log_activity(
                action_type="action.requested",
                summary=f"Created action request: {record.title}",
                risk_level=record.risk_level,
                status=record.status.value,
                details={"action_id": record.id},
            )
            if record.status is ActionStatus.BLOCKED:
                return "這個動作被政策標記為 **禁止**，不會進入批准或執行流程。"
            return (
                f"已建立動作提案：**{record.title}**。風險等級是 "
                f"**{record.risk_level.value}**；目前只等待批准，尚未執行外部操作。"
            )

        if intent.name == "daily_briefing":
            open_tasks = [
                task for task in self.store.list_tasks(limit=50)
                if task.status is not TaskStatus.DONE
            ]
            recent_memories = self.store.list_memories(limit=5)
            pending = self.store.list_action_requests(
                status=ActionStatus.PENDING,
                limit=20,
            )
            self.store.log_activity(
                action_type="briefing.generated",
                summary="Generated founder daily briefing.",
                risk_level=RiskLevel.READ_ONLY,
                details={
                    "open_task_count": len(open_tasks),
                    "memory_count": len(recent_memories),
                    "pending_approval_count": len(pending),
                },
            )
            if not open_tasks and not recent_memories and not pending:
                return (
                    "目前沒有已記錄的待辦、近期決策或待批准提案。"
                    "你可以說「新增待辦：……」、「記住：……」或"
                    "「建立提案：……」開始建立公司脈絡。"
                )
            lines = [f"### 今日 {PERSONAL_OS_NAME} Briefing"]
            if open_tasks:
                lines.append(f"\n**未完成事項：{len(open_tasks)} 項**")
                for task in open_tasks[:8]:
                    project = f" · {task.project}" if task.project else ""
                    lines.append(f"- P{task.priority} · {task.title}{project}")
            if pending:
                lines.append(f"\n**等待批准：{len(pending)} 項**")
                for request in pending[:5]:
                    lines.append(f"- {request.risk_level.value} · {request.title}")
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
                    f"- **{memory.scope.value}/{memory.category.value}/"
                    f"{memory.visibility.value}** · {memory.content}{project}"
                )
            return "\n".join(lines)

        if intent.name == "list_tasks":
            open_tasks = [
                task for task in self.store.list_tasks(limit=100)
                if task.status is not TaskStatus.DONE
            ]
            self.store.log_activity(
                action_type="task.listed",
                summary="Listed open tasks.",
                risk_level=RiskLevel.READ_ONLY,
                details={"count": len(open_tasks)},
            )
            if not open_tasks:
                return "目前沒有未完成待辦。"
            lines = ["### 未完成待辦"]
            for task in open_tasks:
                project = f" · {task.project}" if task.project else ""
                approval = " · 需創辦人批准" if task.approval_required else ""
                lines.append(
                    f"- **P{task.priority} · {task.status.value}** · "
                    f"{task.title}{project}{approval}"
                )
            return "\n".join(lines)

        if intent.name == "invalid_memory":
            return "要記住的內容是空的。請說「記住：你的決策或規則」。"
        if intent.name == "invalid_task":
            return "待辦內容是空的。請說「新增待辦：要完成的事情」。"
        if intent.name == "invalid_action":
            return "提案內容是空的。請說「建立提案：要做的事情」。"
        if intent.name == "empty":
            return "請輸入一個問題或任務。"
        raise ValueError(f"Unsupported local intent: {intent.name}")
