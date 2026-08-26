#!/usr/bin/env python3
"""Private Streamlit control center for Youchen AI OS and EcoFixer AI OS."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import streamlit as st

from founder_company_ai.assistant import FounderCompanyAssistant
from founder_company_ai.branding import COMPANY_OS_NAME, PERSONAL_OS_NAME, WAKE_PHRASE
from founder_company_ai.config import Settings
from founder_company_ai.models import (
    ActionStatus,
    MemoryCategory,
    RiskLevel,
    Scope,
    TaskStatus,
    Visibility,
)
from founder_company_ai.providers.openai_provider import OpenAIProvider
from founder_company_ai.router import CommandRouter, infer_action_risk
from founder_company_ai.services.actions import ActionService
from founder_company_ai.storage import SQLiteStore


@dataclass(slots=True)
class Runtime:
    settings: Settings
    store: SQLiteStore
    assistant: FounderCompanyAssistant
    provider: OpenAIProvider | None
    provider_error: str | None


@st.cache_resource
def build_runtime() -> Runtime:
    settings = Settings.from_env()
    store = SQLiteStore(settings.database_path)
    provider = None
    provider_error = None
    if settings.openai_api_key:
        try:
            provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                transcribe_model=settings.transcribe_model,
            )
        except Exception as exc:
            provider_error = f"{type(exc).__name__}: {exc}"
    assistant = FounderCompanyAssistant(
        store=store,
        router=CommandRouter(),
        actions=ActionService(store),
        provider=provider,
        allow_cloud_memory_context=settings.allow_cloud_memory_context,
    )
    return Runtime(settings, store, assistant, provider, provider_error)


def heading(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def send(runtime: Runtime, text: str) -> None:
    runtime.assistant.handle(
        message=text,
        conversation_id=runtime.settings.default_conversation_id,
    )


def home(runtime: Runtime) -> None:
    heading(PERSONAL_OS_NAME, f"Founder private core · Company workspace: {COMPANY_OS_NAME}")
    counts = runtime.store.counts()
    columns = st.columns(5)
    for column, key, label in zip(
        columns,
        ("contexts", "memories", "open_tasks", "pending_approvals", "activities"),
        ("脈絡", "記憶", "未完成", "待批准", "活動"),
    ):
        column.metric(label, counts[key])

    if runtime.provider is None:
        st.info("本機安全模式：脈絡、記憶、待辦、批准與稽核可用；模型與轉錄未連線。")
    elif runtime.settings.allow_cloud_memory_context:
        st.warning("雲端長期脈絡已開啟，請只儲存允許傳送的內容。")
    else:
        st.success("模型已連線；結構化長期脈絡與本機指令預設留在本機。")

    left, right = st.columns(2)
    with left:
        st.subheader("未完成事項")
        tasks = [
            item for item in runtime.store.list_tasks(limit=8)
            if item.status is not TaskStatus.DONE
        ]
        if not tasks:
            st.caption("目前沒有待辦。")
        for item in tasks:
            st.markdown(f"- **P{item.priority}** · {item.title}")
    with right:
        st.subheader("等待批准")
        requests = runtime.store.list_action_requests(status=ActionStatus.PENDING, limit=8)
        if not requests:
            st.caption("目前沒有等待批准的動作。")
        for item in requests:
            st.markdown(f"- **{item.risk_level.value}** · {item.title}")


def chat(runtime: Runtime) -> None:
    heading("Chat + Voice", f"按下說話；預定喚醒詞是「{WAKE_PHRASE}」。喚醒不等於批准。")
    st.caption("指令：`記住：…`、`新增待辦：…`、`建立提案：…`、`今天公司有什麼事情？`")
    messages = runtime.store.list_messages(runtime.settings.default_conversation_id, limit=60)
    if not messages:
        with st.chat_message("assistant"):
            st.markdown(f"我是 {PERSONAL_OS_NAME}。你可以交代私人、公司或專案工作。")
    for message in messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    with st.expander("語音控制"):
        audio = st.audio_input("錄製語音指令", sample_rate=16000)
        data = audio.getvalue() if audio is not None else b""
        digest = hashlib.sha256(data).hexdigest() if data else ""
        repeated = digest and digest == st.session_state.get("last_voice_hash")
        if runtime.provider is None:
            st.caption("語音轉錄需要設定 `OPENAI_API_KEY`。")
        if st.button(
            "轉錄並執行",
            disabled=audio is None or runtime.provider is None or bool(repeated),
            use_container_width=True,
        ):
            try:
                transcript = runtime.provider.transcribe(
                    audio_bytes=data,
                    filename=getattr(audio, "name", "voice.wav"),
                )
                st.session_state.last_voice_hash = digest
                send(runtime, transcript)
                st.rerun()
            except Exception as exc:
                st.error(f"語音轉錄失敗：{type(exc).__name__}")

    prompt = st.chat_input("跟你的 AI 說話…")
    if prompt:
        send(runtime, prompt)
        st.rerun()


def context_page(runtime: Runtime) -> None:
    heading("Founder & Company", "建立 founder、company、project 三個明確脈絡域。")
    with st.form("context", clear_on_submit=True):
        domain = st.selectbox("範圍", list(Scope), format_func=lambda item: item.value)
        key = st.text_input("欄位", placeholder="communication_style / company_name / priority")
        value = st.text_area("內容")
        visibility_options = (
            [Visibility.FOUNDER_ONLY] if domain is Scope.FOUNDER else list(Visibility)
        )
        visibility = st.selectbox(
            "可見性", visibility_options, format_func=lambda item: item.value
        )
        if st.form_submit_button("儲存", use_container_width=True):
            try:
                record = runtime.store.upsert_context(
                    domain=domain, key=key, value=value, visibility=visibility
                )
                runtime.store.log_activity(
                    action_type="context.upserted",
                    summary=f"Updated context: {record.domain.value}/{record.key}",
                    risk_level=RiskLevel.REVERSIBLE,
                    details={"context_id": record.id},
                )
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    for item in runtime.store.list_context(limit=100):
        with st.container(border=True):
            st.markdown(f"**{item.domain.value} / {item.key}** · `{item.visibility.value}`")
            st.write(item.value)


def memory_page(runtime: Runtime) -> None:
    heading("Memory", "Founder 記憶由資料層強制保持 founder-only。")
    with st.form("memory", clear_on_submit=True):
        content = st.text_area("內容")
        scope = st.selectbox("範圍", list(Scope), format_func=lambda item: item.value)
        category = st.selectbox(
            "類型", list(MemoryCategory), format_func=lambda item: item.value
        )
        visibility_options = (
            [Visibility.FOUNDER_ONLY] if scope is Scope.FOUNDER else list(Visibility)
        )
        visibility = st.selectbox(
            "可見性", visibility_options, format_func=lambda item: item.value
        )
        project = st.text_input("專案（選填）")
        if st.form_submit_button("儲存", use_container_width=True):
            try:
                record = runtime.store.add_memory(
                    content=content,
                    scope=scope,
                    category=category,
                    visibility=visibility,
                    project=project or None,
                )
                runtime.store.log_activity(
                    action_type="memory.created",
                    summary=f"Created {record.category.value} memory.",
                    risk_level=RiskLevel.REVERSIBLE,
                    details={"memory_id": record.id},
                )
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    for item in runtime.store.list_memories(limit=100):
        with st.container(border=True):
            st.markdown(
                f"**{item.scope.value}/{item.category.value}** · `{item.visibility.value}`"
                + (f" · {item.project}" if item.project else "")
            )
            st.write(item.content)


def tasks_page(runtime: Runtime) -> None:
    heading("Tasks", "追蹤 founder、company 與 project 工作。")
    with st.form("task", clear_on_submit=True):
        title = st.text_input("待辦")
        scope = st.selectbox("範圍", list(Scope), format_func=lambda item: item.value)
        project = st.text_input("專案（選填）")
        priority = st.selectbox("優先級", [1, 2, 3], index=1)
        approval_required = st.checkbox("完成前需要創辦人批准")
        if st.form_submit_button("建立", use_container_width=True):
            try:
                record = runtime.store.add_task(
                    title=title,
                    scope=scope,
                    project=project or None,
                    priority=priority,
                    approval_required=approval_required,
                )
                runtime.store.log_activity(
                    action_type="task.created",
                    summary=f"Created task: {record.title}",
                    risk_level=RiskLevel.REVERSIBLE,
                    details={"task_id": record.id},
                )
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    for item in runtime.store.list_tasks(limit=100):
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.markdown(
                f"**P{item.priority} · {item.title}**\n\n"
                f"`{item.scope.value}` · `{item.status.value}`"
            )
            options = list(TaskStatus)
            status = right.selectbox(
                "狀態",
                options,
                index=options.index(item.status),
                format_func=lambda value: value.value,
                key=f"task_{item.id}",
                label_visibility="collapsed",
            )
            if status is not item.status and right.button(
                "更新", key=f"task_update_{item.id}"
            ):
                runtime.store.update_task_status(item.id, status)
                runtime.store.log_activity(
                    action_type="task.status_changed",
                    summary=f"Changed task status: {item.title}",
                    risk_level=RiskLevel.REVERSIBLE,
                    details={"task_id": item.id, "to": status.value},
                )
                st.rerun()


def approvals_page(runtime: Runtime) -> None:
    heading("Approvals", "批准只授權提案；V1 不會假裝外部動作已執行。")
    with st.form("approval", clear_on_submit=True):
        description = st.text_area("動作提案", placeholder="例如：Merge 已通過測試的 PR")
        if st.form_submit_button("建立提案", use_container_width=True):
            risk = infer_action_risk(description)
            try:
                record = runtime.store.create_action_request(
                    title=description[:120],
                    description=description,
                    risk_level=risk,
                    payload={"requested_text": description},
                )
                runtime.store.log_activity(
                    action_type="action.requested",
                    summary=f"Created action request: {record.title}",
                    risk_level=record.risk_level,
                    status=record.status.value,
                    details={"action_id": record.id},
                )
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    for item in runtime.store.list_action_requests(limit=100):
        with st.container(border=True):
            st.markdown(
                f"**{item.title}** · `{item.risk_level.value}` · `{item.status.value}`"
            )
            if item.status is ActionStatus.PENDING:
                approve, reject = st.columns(2)
                if approve.button(
                    "批准", key=f"approve_{item.id}", use_container_width=True
                ):
                    runtime.store.update_action_status(item.id, ActionStatus.APPROVED)
                    runtime.store.log_activity(
                        action_type="action.approved",
                        summary=f"Approved: {item.title}",
                        risk_level=item.risk_level,
                        details={"action_id": item.id, "executed": False},
                    )
                    st.rerun()
                if reject.button(
                    "拒絕", key=f"reject_{item.id}", use_container_width=True
                ):
                    runtime.store.update_action_status(item.id, ActionStatus.REJECTED)
                    runtime.store.log_activity(
                        action_type="action.rejected",
                        summary=f"Rejected: {item.title}",
                        risk_level=item.risk_level,
                        details={"action_id": item.id},
                    )
                    st.rerun()
            elif item.status is ActionStatus.APPROVED:
                st.info("已批准；尚未連接外部執行工具，因此沒有實際執行。")
            elif item.status is ActionStatus.BLOCKED:
                st.error("此動作被政策禁止，不能批准。")


def activity_page(runtime: Runtime) -> None:
    heading("Activity", "所有本機變更與批准都留下稽核紀錄。")
    for item in runtime.store.list_activity(limit=200):
        with st.container(border=True):
            st.markdown(
                f"**{item.action_type}** · `{item.risk_level.value}` · `{item.status}`"
            )
            st.write(item.summary)
            st.caption(item.created_at)
            if item.details:
                st.json(item.details)


def settings_page(runtime: Runtime) -> None:
    heading("Settings", "模型可替換；權限與資料邊界不可交給模型自行決定。")
    st.json(
        {
            "personal_os": PERSONAL_OS_NAME,
            "company_os": COMPANY_OS_NAME,
            "wake_phrase": WAKE_PHRASE,
            "timezone": runtime.settings.timezone,
            "provider_connected": runtime.provider is not None,
            "provider_error": runtime.provider_error,
            "model": runtime.settings.openai_model,
            "transcribe_model": runtime.settings.transcribe_model,
            "database": str(runtime.settings.database_path),
            "cloud_memory_context": runtime.settings.allow_cloud_memory_context,
        }
    )


def main() -> None:
    st.set_page_config(page_title=PERSONAL_OS_NAME, page_icon="◆", layout="wide")
    runtime = build_runtime()
    with st.sidebar:
        st.title(PERSONAL_OS_NAME)
        st.caption(f"Private founder core · {COMPANY_OS_NAME}")
        page = st.radio(
            "Navigation",
            [
                "Home",
                "Chat",
                "Founder & Company",
                "Memory",
                "Tasks",
                "Approvals",
                "Activity",
                "Settings",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("AI connected" if runtime.provider else "Local safe mode")
        st.caption(
            "Cloud memory on"
            if runtime.settings.allow_cloud_memory_context
            else "Memory local"
        )

    pages = {
        "Home": home,
        "Chat": chat,
        "Founder & Company": context_page,
        "Memory": memory_page,
        "Tasks": tasks_page,
        "Approvals": approvals_page,
        "Activity": activity_page,
        "Settings": settings_page,
    }
    pages[page](runtime)


if __name__ == "__main__":
    main()
