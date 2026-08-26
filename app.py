#!/usr/bin/env python3
"""Youchen AI OS and EcoFixer AI OS Streamlit application."""

from __future__ import annotations

import hashlib
import html
from dataclasses import dataclass

import streamlit as st

from founder_company_ai.assistant import FounderCompanyAssistant
from founder_company_ai.branding import COMPANY_OS_NAME, PERSONAL_OS_NAME, WAKE_PHRASE
from founder_company_ai.config import Settings
from founder_company_ai.models import (
    MemoryCategory,
    RiskLevel,
    Scope,
    TaskStatus,
    Visibility,
)
from founder_company_ai.providers.openai_provider import OpenAIProvider
from founder_company_ai.router import CommandRouter
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
    provider: OpenAIProvider | None = None
    provider_error: str | None = None

    if settings.openai_api_key:
        try:
            provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                transcribe_model=settings.transcribe_model,
            )
        except Exception as exc:  # surfaced safely in Settings
            provider_error = f"{type(exc).__name__}: {exc}"

    assistant = FounderCompanyAssistant(
        store=store,
        router=CommandRouter(),
        actions=ActionService(store),
        provider=provider,
        allow_cloud_memory_context=settings.allow_cloud_memory_context,
    )
    return Runtime(
        settings=settings,
        store=store,
        assistant=assistant,
        provider=provider,
        provider_error=provider_error,
    )


CSS = """
<style>
.block-container {max-width: 1080px; padding-top: 2rem; padding-bottom: 5rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(255,255,255,.08);}
.hero {
    padding: 2rem 2.2rem;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,.09);
    background: linear-gradient(145deg, rgba(110,168,254,.12), rgba(255,255,255,.025));
    margin-bottom: 1.2rem;
}
.eyebrow {font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; opacity:.62;}
.hero h1 {font-size:2.45rem; line-height:1.08; margin:.45rem 0 .65rem;}
.muted {opacity:.67;}
.card {
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(255,255,255,.025);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin: .55rem 0;
}
.badge {
    display:inline-block;
    padding:.24rem .58rem;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.12);
    font-size:.72rem;
    opacity:.82;
    margin-right:.32rem;
}
.safe {border-color:rgba(74,222,128,.35); color:#86efac;}
.warn {border-color:rgba(250,204,21,.35); color:#fde047;}
.risk {border-color:rgba(248,113,113,.35); color:#fca5a5;}
.small {font-size:.82rem; opacity:.72;}
</style>
"""


def safe(value: object) -> str:
    return html.escape(str(value))


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">Youchen AI OS · Private Founder Interface</div>
          <h1>{safe(title)}</h1>
          <div class="muted">{safe(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home(runtime: Runtime) -> None:
    page_header(
        PERSONAL_OS_NAME,
        f"你的私人 AI 作業系統；公司工作自動進入 {COMPANY_OS_NAME}，兩邊記憶與權限分離。",
    )
    counts = runtime.store.counts()
    provider_status = "AI 已連線" if runtime.provider else "本機安全模式"
    columns = st.columns(4)
    columns[0].metric("啟用記憶", counts["memories"])
    columns[1].metric("未完成事項", counts["open_tasks"])
    columns[2].metric("活動紀錄", counts["activities"])
    columns[3].metric("模式", provider_status)

    st.caption(
        f"預定本機喚醒詞：`{WAKE_PHRASE}`。目前 V1 使用按鍵式語音；背景常駐喚醒屬下一階段。"
    )

    if runtime.provider is None:
        st.info(
            "目前不會呼叫雲端模型。記憶、待辦、活動紀錄和每日摘要仍可使用；"
            "設定 API key 後才啟用生成式對話與語音轉錄。"
        )
    elif not runtime.settings.allow_cloud_memory_context:
        st.success("AI 已連線，但長期記憶仍留在本機，不會自動送入模型。")
    else:
        st.warning("雲端記憶上下文已啟用。請只儲存你允許傳送給模型的內容。")

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("現在要處理")
        tasks = [
            task
            for task in runtime.store.list_tasks(limit=8)
            if task.status is not TaskStatus.DONE
        ]
        if not tasks:
            st.caption("尚無待辦。到 Chat 說「新增待辦：……」即可建立。")
        for task in tasks:
            project = f" · {task.project}" if task.project else ""
            st.markdown(
                f"""
                <div class="card">
                  <span class="badge">P{task.priority}</span>
                  <span class="badge">{safe(task.scope.value)}</span>
                  <strong>{safe(task.title)}</strong>
                  <div class="small">{safe(task.status.value + project)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("近期決策與記憶")
        memories = runtime.store.list_memories(limit=6)
        if not memories:
            st.caption("尚無記憶。到 Chat 說「記住：……」即可建立。")
        for memory in memories:
            project = f" · {memory.project}" if memory.project else ""
            st.markdown(
                f"""
                <div class="card">
                  <span class="badge">{safe(memory.category.value)}</span>
                  <span class="badge">{safe(memory.visibility.value)}</span>
                  <div>{safe(memory.content)}</div>
                  <div class="small">{safe(memory.scope.value + project)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _send_chat(runtime: Runtime, text: str) -> None:
    runtime.assistant.handle(
        message=text,
        conversation_id=runtime.settings.default_conversation_id,
    )


def render_chat(runtime: Runtime) -> None:
    page_header(
        "Chat",
        f"對 {PERSONAL_OS_NAME} 交代目標；公司內容會路由到 {COMPANY_OS_NAME}。",
    )
    st.caption(
        "直接指令：`記住：……`、`新增待辦：……`、`今天公司有什麼事情？`、"
        "`列出記憶`、`列出待辦`"
    )

    messages = runtime.store.list_messages(
        runtime.settings.default_conversation_id,
        limit=60,
    )
    if not messages:
        with st.chat_message("assistant"):
            st.markdown(
                f"我是 {PERSONAL_OS_NAME}。你可以處理私人事項，或直接交代 "
                f"{COMPANY_OS_NAME} 的公司工作。"
            )
    else:
        for message in messages:
            with st.chat_message(message.role):
                st.markdown(message.content)

    with st.expander("語音控制（按鍵式）", expanded=False):
        st.caption(
            f"目前先按鍵錄音。下一階段會加入本機常駐喚醒詞 `{WAKE_PHRASE}`、VAD 與語音回覆。"
        )
        if runtime.provider is None:
            st.caption("語音錄製可用；語音轉錄需要設定 API key。")
        voice = st.audio_input(
            "按下麥克風說話",
            sample_rate=16000,
            key="founder_voice",
        )
        voice_bytes = voice.getvalue() if voice is not None else b""
        voice_hash = hashlib.sha256(voice_bytes).hexdigest() if voice_bytes else None
        already_sent = voice_hash and voice_hash == st.session_state.get("last_voice_hash")

        if already_sent:
            st.caption("這段語音已送出；重新錄音後可再次傳送。")

        if st.button(
            "轉錄並送出",
            disabled=voice is None or runtime.provider is None or bool(already_sent),
            use_container_width=True,
        ):
            try:
                transcript = runtime.provider.transcribe(
                    audio_bytes=voice_bytes,
                    filename=getattr(voice, "name", "voice.wav"),
                )
                st.session_state.last_voice_hash = voice_hash
                st.session_state.last_transcript = transcript
                _send_chat(runtime, transcript)
                st.rerun()
            except Exception as exc:
                st.error(f"語音轉錄失敗：{type(exc).__name__}: {exc}")

        if st.session_state.get("last_transcript"):
            st.caption(f"上次語音：{st.session_state.last_transcript}")

    prompt = st.chat_input(f"跟 {PERSONAL_OS_NAME} 說話…")
    if prompt:
        _send_chat(runtime, prompt)
        st.rerun()


def render_memory(runtime: Runtime) -> None:
    page_header(
        "Memory",
        f"{PERSONAL_OS_NAME}、{COMPANY_OS_NAME} 與專案記憶分開保存。",
    )
    with st.form("add_memory", clear_on_submit=True):
        content = st.text_area("內容", placeholder="例如：金額與抽成比例必須可調整，UI 先保留位置。")
        c1, c2, c3 = st.columns(3)
        scope = c1.selectbox("範圍", list(Scope), format_func=lambda item: item.value)
        category = c2.selectbox(
            "類型",
            list(MemoryCategory),
            format_func=lambda item: item.value,
        )
        visibility = c3.selectbox(
            "可見性",
            list(Visibility),
            format_func=lambda item: item.value,
        )
        project = st.text_input("專案（選填）")
        submitted = st.form_submit_button("儲存記憶", use_container_width=True)
        if submitted:
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
                    summary=f"Created memory from Memory page: {record.category.value}.",
                    risk_level=RiskLevel.REVERSIBLE,
                    details={"memory_id": record.id},
                )
                st.success("記憶已儲存。")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    st.subheader("啟用中的記憶")
    memories = runtime.store.list_memories(limit=100)
    if not memories:
        st.caption("尚無記憶。")
    for memory in memories:
        project = f" · {memory.project}" if memory.project else ""
        st.markdown(
            f"""
            <div class="card">
              <span class="badge">{safe(memory.scope.value)}</span>
              <span class="badge">{safe(memory.category.value)}</span>
              <span class="badge">{safe(memory.visibility.value)}</span>
              <div style="margin-top:.55rem">{safe(memory.content)}</div>
              <div class="small">{safe(memory.created_at + project)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_tasks(runtime: Runtime) -> None:
    page_header(
        "Tasks",
        "先把工作與責任看清楚；V1 只執行本機可逆操作。",
    )
    with st.form("add_task", clear_on_submit=True):
        title = st.text_input("待辦", placeholder="例如：完成權限模型與 founder-only memory 測試")
        c1, c2, c3 = st.columns(3)
        scope = c1.selectbox("範圍", list(Scope), format_func=lambda item: item.value)
        priority = c2.selectbox("優先級", [1, 2, 3], index=1)
        approval_required = c3.checkbox("完成前需創辦人批准")
        project = st.text_input("專案（選填）")
        submitted = st.form_submit_button("建立待辦", use_container_width=True)
        if submitted:
            try:
                task = runtime.store.add_task(
                    title=title,
                    scope=scope,
                    project=project or None,
                    priority=priority,
                    approval_required=approval_required,
                )
                runtime.store.log_activity(
                    action_type="task.created",
                    summary=f"Created task from Tasks page: {task.title}",
                    risk_level=RiskLevel.REVERSIBLE,
                    details={"task_id": task.id},
                )
                st.success("待辦已建立。")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    tasks = runtime.store.list_tasks(limit=100)
    if not tasks:
        st.caption("尚無待辦。")
        return

    for task in tasks:
        with st.container(border=True):
            left, right = st.columns([4, 1.2])
            with left:
                project = f" · {task.project}" if task.project else ""
                approval = " · 需批准" if task.approval_required else ""
                st.markdown(f"**{task.title}**")
                st.caption(
                    f"P{task.priority} · {task.scope.value} · {task.status.value}"
                    f"{project}{approval}"
                )
            with right:
                options = list(TaskStatus)
                current_index = options.index(task.status)
                new_status = st.selectbox(
                    "狀態",
                    options,
                    index=current_index,
                    format_func=lambda item: item.value,
                    key=f"status_{task.id}",
                    label_visibility="collapsed",
                )
                if new_status is not task.status and st.button(
                    "更新",
                    key=f"update_{task.id}",
                    use_container_width=True,
                ):
                    runtime.store.update_task_status(task.id, new_status)
                    runtime.store.log_activity(
                        action_type="task.status_changed",
                        summary=f"Changed task status: {task.title}",
                        risk_level=RiskLevel.REVERSIBLE,
                        details={
                            "task_id": task.id,
                            "from": task.status.value,
                            "to": new_status.value,
                        },
                    )
                    st.rerun()


def render_activity(runtime: Runtime) -> None:
    page_header(
        "Activity",
        "AI 與本機工具做過的事情都必須留下可追蹤紀錄。",
    )
    activities = runtime.store.list_activity(limit=200)
    if not activities:
        st.caption("尚無活動紀錄。")
        return
    for activity in activities:
        badge_class = {
            RiskLevel.READ_ONLY: "safe",
            RiskLevel.DRAFT: "safe",
            RiskLevel.REVERSIBLE: "warn",
            RiskLevel.APPROVAL_REQUIRED: "risk",
            RiskLevel.PROHIBITED: "risk",
        }[activity.risk_level]
        st.markdown(
            f"""
            <div class="card">
              <span class="badge {badge_class}">{safe(activity.risk_level.value)}</span>
              <span class="badge">{safe(activity.status)}</span>
              <strong>{safe(activity.action_type)}</strong>
              <div style="margin-top:.45rem">{safe(activity.summary)}</div>
              <div class="small">{safe(activity.created_at)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if activity.details:
            with st.expander("詳細資料"):
                st.json(activity.details)


def render_settings(runtime: Runtime) -> None:
    page_header(
        "Settings",
        "模型可以更換；資料邊界、權限與稽核規則不能依賴模型自己決定。",
    )
    st.subheader("Identity")
    st.write(
        {
            "personal_os": PERSONAL_OS_NAME,
            "company_os": COMPANY_OS_NAME,
            "wake_phrase": WAKE_PHRASE,
            "always_on_wake_word": "planned",
        }
    )

    st.subheader("AI Provider")
    st.write(
        {
            "connected": runtime.provider is not None,
            "model": runtime.settings.openai_model,
            "transcribe_model": runtime.settings.transcribe_model,
            "api_key": "configured" if runtime.settings.openai_api_key else "not configured",
            "provider_error": runtime.provider_error,
        }
    )

    st.subheader("Privacy")
    st.write(
        {
            "database": str(runtime.settings.database_path),
            "cloud_memory_context": runtime.settings.allow_cloud_memory_context,
            "default_conversation": runtime.settings.default_conversation_id,
        }
    )
    if runtime.settings.allow_cloud_memory_context:
        st.warning("長期記憶可能被納入模型請求。只應儲存經批准可傳送的內容。")
    else:
        st.success("長期記憶維持本機，不自動送入模型。")

    st.subheader("V1 Authority")
    rows = [
        ("讀取本機記憶／任務", "直接執行", "read_only"),
        ("新增記憶／待辦", "直接執行並記錄", "reversible"),
        ("建立草稿", "下一階段", "draft"),
        ("發信、Merge、修改正式環境", "執行前必須批准", "approval_required"),
        ("刪除正式資料、未授權付款", "禁止", "prohibited"),
    ]
    st.table(
        {
            "能力": [row[0] for row in rows],
            "規則": [row[1] for row in rows],
            "風險": [row[2] for row in rows],
        }
    )


def main() -> None:
    st.set_page_config(
        page_title=PERSONAL_OS_NAME,
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)
    runtime = build_runtime()

    with st.sidebar:
        st.title(PERSONAL_OS_NAME)
        st.caption(f"Company workspace · {COMPANY_OS_NAME}")
        page = st.radio(
            "Navigation",
            ["Home", "Chat", "Memory", "Tasks", "Activity", "Settings"],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown(
            f'<span class="badge safe">Wake: {safe(WAKE_PHRASE)}</span>',
            unsafe_allow_html=True,
        )
        if runtime.provider:
            st.markdown('<span class="badge safe">AI connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge warn">Local safe mode</span>', unsafe_allow_html=True)
        if runtime.settings.allow_cloud_memory_context:
            st.markdown('<span class="badge warn">Cloud memory on</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge safe">Memory local</span>', unsafe_allow_html=True)

    pages = {
        "Home": render_home,
        "Chat": render_chat,
        "Memory": render_memory,
        "Tasks": render_tasks,
        "Activity": render_activity,
        "Settings": render_settings,
    }
    pages[page](runtime)


if __name__ == "__main__":
    main()
