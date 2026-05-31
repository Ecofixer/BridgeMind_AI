#!/usr/bin/env python3
"""BridgeMind AI — Apple × Linear × Notion × Palantir 智慧橋梁決策平台"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "raw_documents"
INPUTS = DATA / "bridge_inputs"
KB = DATA / "knowledge_base"
OUT = ROOT / "outputs"
EXPORTS = ROOT / "exports"
PROFILE_PATH = INPUTS / "zengwen_bridge_profile.json"
NOTES_PATH = KB / "zengwen_bridge_notes.md"
SOURCE_LINKS_PATH = DATA / "source_links.json"

SOURCE_CATEGORIES = [
    "環評資料",
    "可行性評估",
    "橋梁案例",
    "法規資料",
    "工程資料",
    "大地資料",
    "水文排水資料",
    "結構資料",
    "BIM 資料",
    "AI 技術資料",
    "簡報與報告資料",
    "其他資料",
]

CATEGORY_FOLDER_MAP = {
    "環評資料": "environmental_reports",
    "可行性評估": "feasibility_reports",
    "橋梁案例": "bridge_cases",
    "法規資料": "regulations",
    "工程資料": "engineering",
    "大地資料": "geotechnical",
    "水文排水資料": "hydrology_drainage",
    "結構資料": "structural",
    "BIM 資料": "bim",
    "AI 技術資料": "ai_technology",
    "簡報與報告資料": "presentation_reports",
    "其他資料": "others",
}

CORE_DATA_CATEGORIES = ("環評資料", "可行性評估", "橋梁案例", "法規資料")

PAGES = [("project", "Project"), ("data", "Data"), ("analysis", "Analysis"), ("output", "Output")]

PIPELINE = [
    ("research", "research_summary.md"),
    ("engineering", "engineering_analysis.md"),
    ("environment", "environmental_sustainability.md"),
    ("design", "design_bim_visualization.md"),
    ("ai", "ai_integration_plan.md"),
    ("cost", "cost_schedule_analysis.md"),
    ("report", "final_report.md"),
]

PRIMARY = {
    "00_bridgemind_recommendation.md": ("決策建議書", "BridgeMind 綜合決策建議"),
    "01_executive_summary.md": ("主管摘要", "Executive Summary"),
    "02_decision_dashboard.md": ("決策儀表板", "Decision Dashboard"),
}

TECH = {
    "research_summary.md": "資料研究摘要",
    "engineering_analysis.md": "工程分析",
    "environmental_sustainability.md": "環境永續",
    "design_bim_visualization.md": "設計與 BIM 規劃",
    "ai_integration_plan.md": "AI 導入策略",
    "cost_schedule_analysis.md": "經費與工期",
    "final_report.md": "最終報告",
    "ppt_outline.md": "簡報大綱",
    "bim_parameters.json": "BIM 參數",
}

ALL_OUTPUTS = list(PRIMARY.keys()) + list(TECH.keys())

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.stApp { background: #050505; color: #F5F5F7; }
.block-container { max-width: 920px; padding-top: 2.5rem; padding-bottom: 4rem; }
[data-testid="stSidebar"] {
  background: #0A0A0A;
  border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] .block-container { padding-top: 2rem; max-width: 100%; }
#MainMenu, footer, header { visibility: hidden; }

.display { font-size: 3rem; font-weight: 600; letter-spacing: -0.03em; line-height: 1.1; color: #F5F5F7; margin: 0; }
.display-sm { font-size: 1.75rem; font-weight: 600; letter-spacing: -0.02em; color: #F5F5F7; margin: 0; }
.subhead { font-size: 1.05rem; color: #A1A1AA; margin-top: 0.5rem; font-weight: 400; }
.caption { font-size: 0.8rem; color: #71717A; letter-spacing: 0.02em; }

.glass {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  padding: 1.75rem 2rem;
  margin-bottom: 1rem;
}
.glass-sm {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 1.25rem 1.5rem;
}
.glass-hero {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 28px;
  padding: 3rem 2.5rem;
  text-align: center;
  margin: 2rem 0;
}

.status-pill {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 500;
  color: #A1A1AA;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
}
.status-pill.ready { color: #30D158; border-color: rgba(48,209,88,0.3); background: rgba(48,209,88,0.08); }
.status-pill.warn { color: #FFD60A; border-color: rgba(255,214,10,0.3); background: rgba(255,214,10,0.08); }

.readiness-num {
  font-size: 4rem;
  font-weight: 600;
  letter-spacing: -0.04em;
  color: #F5F5F7;
  line-height: 1;
}
.readiness-label { font-size: 0.8rem; color: #71717A; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }

.mini-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.mini-cell {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1rem 1.1rem;
}
.mini-cell .k { font-size: 0.7rem; color: #71717A; text-transform: uppercase; letter-spacing: 0.06em; }
.mini-cell .v { font-size: 0.95rem; color: #F5F5F7; margin-top: 0.35rem; font-weight: 500; }

.pipeline {
  display: flex; flex-wrap: wrap; gap: 1.25rem; justify-content: flex-start;
  padding: 1rem 0; opacity: 0.55;
}
.p-step { display: flex; align-items: center; gap: 0.45rem; font-size: 0.75rem; color: #71717A; }
.dot { width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid #52525B; background: transparent; }
.dot.done { background: #30D158; border-color: #30D158; }

.section-label { font-size: 0.7rem; color: #52525B; text-transform: uppercase; letter-spacing: 0.12em; margin: 2rem 0 1rem; }

div.stButton > button[kind="primary"] {
  background: #0071E3 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 980px !important;
  padding: 0.65rem 1.75rem !important;
  font-weight: 500 !important;
  font-size: 0.95rem !important;
  box-shadow: none !important;
}
div.stButton > button[kind="primary"]:hover { background: #0077ED !important; }
div.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.06) !important;
  color: #F5F5F7 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 980px !important;
}

/* ── Form controls (Windows / Streamlit Cloud / BaseWeb) ── */
div[data-baseweb="input"] {
  background-color: #111111 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
}
div[data-baseweb="input"] > div {
  background-color: #111111 !important;
  border-radius: 14px !important;
}
div[data-baseweb="input"] input {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
  caret-color: #F5F5F7 !important;
  -webkit-text-fill-color: #F5F5F7 !important;
}
div[data-baseweb="input"] input::placeholder {
  color: #8E8E93 !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #8E8E93 !important;
}

textarea,
.stTextArea textarea,
[data-testid="stTextArea"] textarea {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
  caret-color: #F5F5F7 !important;
  -webkit-text-fill-color: #F5F5F7 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
}
textarea::placeholder,
.stTextArea textarea::placeholder {
  color: #8E8E93 !important;
  opacity: 1 !important;
}

div[data-baseweb="select"] {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
}
div[data-baseweb="select"] > div {
  background-color: #111111 !important;
  border-radius: 14px !important;
}
div[data-baseweb="select"] * {
  color: #F5F5F7 !important;
}
div[data-baseweb="select"] svg {
  fill: #A1A1AA !important;
}

div[data-baseweb="popover"] {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
}

ul[role="listbox"] {
  background-color: #111111 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
}
li[role="option"] {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
  background-color: rgba(0,113,227,0.18) !important;
  color: #FFFFFF !important;
}

div[data-baseweb="tag"] {
  background-color: rgba(0,113,227,0.2) !important;
  border: 1px solid rgba(0,113,227,0.35) !important;
}
div[data-baseweb="tag"] span {
  color: #F5F5F7 !important;
}

section[data-testid="stFileUploader"] {
  background-color: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 18px !important;
}
section[data-testid="stFileUploader"] * {
  color: #F5F5F7 !important;
}

.stTextInput input,
.stNumberInput input,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
  caret-color: #F5F5F7 !important;
  -webkit-text-fill-color: #F5F5F7 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
}
.stSelectbox > div > div,
[data-testid="stSelectbox"] > div > div {
  background-color: #111111 !important;
  color: #F5F5F7 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
}

[data-testid="stWidgetLabel"],
label[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label {
  color: #A1A1AA !important;
}

input:focus,
textarea:focus,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within {
  outline: none !important;
  border-color: #0071E3 !important;
  box-shadow: 0 0 0 3px rgba(0,113,227,0.18) !important;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
textarea:-webkit-autofill,
textarea:-webkit-autofill:focus {
  -webkit-box-shadow: 0 0 0 1000px #111111 inset !important;
  -webkit-text-fill-color: #F5F5F7 !important;
  caret-color: #F5F5F7 !important;
  transition: background-color 9999s ease-out 0s;
}

::selection {
  background: rgba(0,113,227,0.35) !important;
  color: #FFFFFF !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }

.nav-brand { font-size: 1rem; font-weight: 600; color: #F5F5F7; margin-bottom: 0.25rem; }
.nav-sub { font-size: 0.7rem; color: #52525B; margin-bottom: 1.5rem; }
.sbf { font-size: 0.65rem; color: #3F3F46; line-height: 1.7; margin-top: 2rem; }

.package-title { font-size: 1rem; font-weight: 600; color: #F5F5F7; margin-bottom: 0.25rem; }
.package-desc { font-size: 0.85rem; color: #71717A; margin-bottom: 1rem; }

.card-preview { font-size: 0.9rem; color: #A1A1AA; line-height: 1.65; max-height: 200px; overflow: hidden; }

.doc-list-header {
  display: grid;
  grid-template-columns: 1fr 120px 72px 56px;
  gap: 0.75rem;
  padding: 0 0.25rem 0.6rem;
  font-size: 0.68rem;
  color: #52525B;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 0.25rem;
}
.doc-row-wrap {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.45rem;
}
.doc-row-wrap:hover { border-color: rgba(255,255,255,0.12); }
.doc-name { font-size: 0.9rem; color: #F5F5F7; font-weight: 500; word-break: break-all; }
.doc-meta { font-size: 0.82rem; color: #A1A1AA; }
.doc-preview-box {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  margin: 0.5rem 0;
  font-size: 0.82rem;
  color: #A1A1AA;
  line-height: 1.55;
}
.doc-preview-box strong { color: #F5F5F7; font-weight: 500; }
.doc-action-label { font-size: 0.75rem; color: #71717A; margin-bottom: 0.35rem; }
.doc-delete-warn {
  font-size: 0.8rem;
  color: #FF9F9A;
  margin: 0.5rem 0 0.25rem;
  line-height: 1.45;
}
div[data-testid="stPopover"] > button {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 8px !important;
  color: #A1A1AA !important;
  font-size: 1rem !important;
  padding: 0.2rem 0.55rem !important;
  min-height: 2rem !important;
}

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin: 1rem 0; }
@media (max-width: 800px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.kpi-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 1.1rem 1.25rem;
}
.kpi-card .n { font-size: 1.75rem; font-weight: 600; color: #F5F5F7; letter-spacing: -0.02em; }
.kpi-card .l { font-size: 0.68rem; color: #71717A; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.35rem; }
.link-url { font-size: 0.78rem; color: #71717A; word-break: break-all; margin-top: 0.25rem; }
.hub-tab-title { font-size: 1.1rem; font-weight: 600; color: #F5F5F7; margin: 0 0 0.35rem; }
.hub-tab-desc { font-size: 0.88rem; color: #71717A; margin: 0 0 1.25rem; line-height: 1.5; }
.warn-hint {
  font-size: 0.85rem; color: #FFD60A;
  background: rgba(255,214,10,0.06);
  border: 1px solid rgba(255,214,10,0.15);
  border-radius: 12px;
  padding: 0.65rem 1rem;
  margin: 0.35rem 0;
}
</style>
"""


# ── Profile & I/O ─────────────────────────────────────────────────────────────
def blank_profile(name: str = "", location: str = "", goal: str = "") -> dict[str, Any]:
    return {
        "project_name": name,
        "system_name": "BridgeMind AI",
        "location": location,
        "project_type": "",
        "bridge_type_goal": goal,
        "river_width": "",
        "bridge_length": "",
        "bridge_width_m": "",
        "design_speed_kmh": "",
        "road_lanes": "",
        "motorcycle_lane_width_m": "",
        "development_area_ha": "",
        "detention_volume_m3": "",
        "soil_type": "",
        "foundation_method": "",
        "wetland": "",
        "route_strategy": [],
        "environment_constraints": [],
        "engineering_constraints": [],
        "bridge_type_candidates": [],
        "design_keywords": [],
        "possible_design_concepts": [],
        "bim_required_elements": [],
        "ai_requirements": {
            "use_rag": False, "use_cnn": False, "use_pinn": False,
            "use_agentic_ai": False, "use_digital_twin": False, "use_generative_ai": False,
        },
    }


def ensure_directories() -> None:
    """建立所有必要資料夾與預設檔案。"""
    for folder_name in CATEGORY_FOLDER_MAP.values():
        (RAW / folder_name).mkdir(parents=True, exist_ok=True)
    for d in [INPUTS, KB, OUT, DATA, EXPORTS / "word", EXPORTS / "ppt", EXPORTS / "images", EXPORTS / "bim"]:
        d.mkdir(parents=True, exist_ok=True)
    if not NOTES_PATH.exists():
        NOTES_PATH.write_text("", encoding="utf-8")
    if not SOURCE_LINKS_PATH.exists():
        with open(SOURCE_LINKS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def ensure_dirs() -> None:
    ensure_directories()


def project_exists() -> bool:
    if not PROFILE_PATH.exists() or PROFILE_PATH.stat().st_size == 0:
        return False
    try:
        with open(PROFILE_PATH, encoding="utf-8") as f:
            return bool(str(json.load(f).get("project_name", "")).strip())
    except (json.JSONDecodeError, OSError):
        return False


def load_profile() -> dict[str, Any] | None:
    if not project_exists():
        return None
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_profile(data: dict[str, Any]) -> None:
    INPUTS.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_project(name: str, location: str, goal: str) -> None:
    save_profile(blank_profile(name.strip(), location.strip(), goal.strip()))


def load_notes() -> str:
    return NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else ""


def save_notes(text: str) -> None:
    KB.mkdir(parents=True, exist_ok=True)
    NOTES_PATH.write_text(text, encoding="utf-8")


def write_out(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")


def read_out(name: str) -> str | None:
    p = OUT / name
    return p.read_text(encoding="utf-8") if p.exists() and p.stat().st_size > 0 else None


def read_json_out(name: str) -> dict | None:
    p = OUT / name
    if p.exists() and p.stat().st_size > 0:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def out_exists(name: str) -> bool:
    p = OUT / name
    return p.exists() and p.stat().st_size > 0


def has_primary_outputs() -> bool:
    return out_exists("00_bridgemind_recommendation.md")


def lines_to_list(t: str) -> list[str]:
    return [ln.strip() for ln in t.splitlines() if ln.strip()]


def list_to_lines(items: list | None) -> str:
    return "\n".join(items or [])


def category_folder_path(category: str) -> Path:
    folder_name = CATEGORY_FOLDER_MAP.get(category, "others")
    return RAW / folder_name


def format_file_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def get_unique_filepath(folder_path: Path, filename: str) -> Path:
    """避免同名覆蓋，必要時自動重新命名。"""
    folder_path.mkdir(parents=True, exist_ok=True)
    target = folder_path / filename
    if not target.exists():
        return target
    stem = Path(filename).stem
    suffix = Path(filename).suffix or ".pdf"
    n = 1
    while True:
        candidate = folder_path / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def get_uploaded_documents() -> list[dict]:
    """掃描所有分類資料夾，回傳 PDF 文件清單。"""
    docs: list[dict] = []
    for category, folder_key in CATEGORY_FOLDER_MAP.items():
        folder_path = RAW / folder_key
        folder_path.mkdir(parents=True, exist_ok=True)
        try:
            entries = sorted(folder_path.iterdir())
        except OSError:
            continue
        for f in entries:
            if not f.is_file() or f.name.startswith(".") or f.suffix.lower() != ".pdf":
                continue
            try:
                size_bytes = f.stat().st_size
            except OSError:
                size_bytes = 0
            docs.append({
                "name": f.name,
                "category": category,
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 1) if size_bytes else 0,
                "size_display": format_file_size(size_bytes),
                "path": str(f.resolve()),
            })
    return sorted(docs, key=lambda d: (d["category"], d["name"].lower()))


def load_source_links() -> list[dict]:
    if not SOURCE_LINKS_PATH.exists():
        return []
    try:
        with open(SOURCE_LINKS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_source_links(links: list[dict]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with open(SOURCE_LINKS_PATH, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)


def add_source_link(title: str, url: str, category: str, note: str) -> tuple[bool, str]:
    title = title.strip()
    url = url.strip()
    note = note.strip()
    if not title:
        return False, "標題不可空白"
    if not url:
        return False, "URL 不可空白"
    if not url.startswith(("http://", "https://")):
        return False, "URL 必須以 http:// 或 https:// 開頭"
    links = load_source_links()
    links.append({
        "id": str(uuid.uuid4()),
        "title": title,
        "url": url,
        "category": category,
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_source_links(links)
    return True, "已儲存網址"


def delete_source_link(link_id: str) -> tuple[bool, str]:
    links = load_source_links()
    new_links = [lnk for lnk in links if lnk.get("id") != link_id]
    if len(new_links) == len(links):
        return False, "找不到此網址資料"
    save_source_links(new_links)
    return True, "已刪除網址"


def get_data_overview() -> dict[str, Any]:
    docs = get_uploaded_documents()
    links = load_source_links()
    notes = load_notes()
    notes_len = len(notes.strip())

    pdf_by_cat = {c: 0 for c in SOURCE_CATEGORIES}
    link_by_cat = {c: 0 for c in SOURCE_CATEGORIES}
    for d in docs:
        cat = d.get("category", "其他資料")
        if cat in pdf_by_cat:
            pdf_by_cat[cat] += 1
    for lnk in links:
        cat = lnk.get("category", "其他資料")
        if cat in link_by_cat:
            link_by_cat[cat] += 1

    covered: set[str] = set()
    for cat in SOURCE_CATEGORIES:
        if pdf_by_cat.get(cat, 0) > 0 or link_by_cat.get(cat, 0) > 0:
            covered.add(cat)

    core_gaps: list[str] = []
    gap_messages = {
        "環評資料": "尚未加入環評資料。",
        "可行性評估": "尚未加入可行性評估資料。",
        "橋梁案例": "尚未加入橋梁案例。",
        "法規資料": "尚未加入法規資料。",
    }
    for cat in CORE_DATA_CATEGORIES:
        if pdf_by_cat.get(cat, 0) == 0 and link_by_cat.get(cat, 0) == 0:
            core_gaps.append(gap_messages[cat])

    return {
        "pdf_count": len(docs),
        "link_count": len(links),
        "notes_length": notes_len,
        "categories_covered": len(covered),
        "pdf_by_cat": pdf_by_cat,
        "link_by_cat": link_by_cat,
        "core_gaps": core_gaps,
        "has_notes": notes_len > 0,
    }


def calculate_data_completeness(
    p: dict, notes: str, pdf_files: list, source_links: list
) -> int:
    """profile 40% + notes 20% + PDF 20% + 網址 20%。"""
    if not has_required_fields(p):
        return 0
    important = [
        "project_name", "location", "bridge_type_goal",
        "river_width", "soil_type", "bridge_width_m",
    ]
    filled = sum(1 for k in important if not empty(p.get(k)))
    score = int(40 * filled / len(important))
    if len(notes.strip()) >= 30:
        score += 20
    if len(pdf_files) > 0:
        score += 20
    if len(source_links) > 0:
        score += 20
    return min(score, 100)


def delete_document(file_path: str) -> tuple[bool, str]:
    """刪除指定文件，回傳 (成功與否, 訊息)。"""
    try:
        path = Path(file_path).resolve()
        raw_root = RAW.resolve()
        if raw_root not in path.parents and path != raw_root:
            return False, "不允許刪除此路徑"
        if not path.is_file():
            return False, "檔案不存在"
        os.remove(path)
        return True, "刪除成功"
    except FileNotFoundError:
        return False, "檔案不存在"
    except PermissionError:
        return False, "沒有刪除權限"
    except OSError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def _doc_session_key(doc: dict) -> str:
    return hashlib.md5(doc["path"].encode("utf-8")).hexdigest()[:12]


def list_pdfs() -> list[dict]:
    """相容舊邏輯：供分析流程使用。"""
    return [
        {"name": d["name"], "category": d["category"], "size": d["size_display"]}
        for d in get_uploaded_documents()
    ]


def pdfs_by_cat() -> dict[str, list[str]]:
    r = {c: [] for c in SOURCE_CATEGORIES}
    for row in get_uploaded_documents():
        cat = row["category"]
        if cat in r:
            r[cat].append(row["name"])
    return r


def links_by_cat() -> dict[str, list[dict]]:
    r = {c: [] for c in SOURCE_CATEGORIES}
    for lnk in load_source_links():
        cat = lnk.get("category", "其他資料")
        if cat in r:
            r[cat].append(lnk)
    return r


def _category_has_data(cat: str, pdfs: dict[str, list[str]], links: list[dict]) -> bool:
    if pdfs.get(cat):
        return True
    return any(lnk.get("category") == cat for lnk in links)


def empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    return len(v) == 0 if isinstance(v, (list, dict)) else False


def _bl(items: list) -> str:
    return "\n".join(f"- {x}" for x in items) if items else ""


def missing_items(p: dict, notes: str, pdfs: dict[str, list[str]]) -> list[str]:
    links = load_source_links()
    m = []
    if not _category_has_data("環評資料", pdfs, links):
        m.append("環評資料")
    if not _category_has_data("可行性評估", pdfs, links):
        m.append("可行性評估")
    if not _category_has_data("橋梁案例", pdfs, links):
        m.append("橋梁案例")
    if not _category_has_data("法規資料", pdfs, links):
        m.append("法規資料")
    if empty(p.get("river_width")):
        m.append("河寬與地形")
    if empty(p.get("soil_type")) and empty(p.get("foundation_method")):
        m.append("地質與基礎")
    if empty(p.get("bridge_width_m")) and empty(p.get("bridge_length")):
        m.append("橋梁尺度")
    if empty(p.get("wetland")) and not p.get("environment_constraints"):
        m.append("環境條件")
    if len(notes.strip()) < 30:
        m.append("知識筆記")
    if not p.get("bridge_type_candidates") and not p.get("possible_design_concepts"):
        m.append("橋型或設計方向")
    return list(dict.fromkeys(m))


def has_required_fields(p: dict) -> bool:
    return all(not empty(p.get(k)) for k in ("project_name", "location", "bridge_type_goal"))


def has_basic_engineering(p: dict) -> bool:
    eng = ["river_width", "soil_type", "foundation_method", "bridge_width_m", "design_speed_kmh"]
    return sum(1 for k in eng if not empty(p.get(k))) >= 3


def has_environment_data(p: dict, notes: str, pdfs: dict) -> bool:
    env_note = any(k in notes for k in ("環", "濕", "生態", "水質"))
    links = load_source_links()
    has_env_source = _category_has_data("環評資料", pdfs, links)
    return (not empty(p.get("wetland")) or bool(p.get("environment_constraints"))) and (
        has_env_source or env_note or len(notes.strip()) >= 50
    )


def has_design_data(p: dict) -> bool:
    return bool(p.get("bridge_type_candidates")) and bool(p.get("design_keywords")) and bool(p.get("bim_required_elements"))


def data_sufficient(p: dict, notes: str, pdfs: dict) -> bool:
    return (
        has_required_fields(p)
        and has_basic_engineering(p)
        and has_environment_data(p, notes, pdfs)
        and has_design_data(p)
        and (len(notes.strip()) >= 30 or sum(len(v) for v in pdfs.values()) >= 1)
    )


def project_readiness(p: dict, notes: str, pdfs: list) -> int:
    links = load_source_links()
    score = calculate_data_completeness(p, notes, pdfs, links)
    if score == 0:
        return 0
    if has_design_data(p) and score >= 60:
        score = min(score + 10, 100)
    if not data_sufficient(p, notes, pdfs_by_cat()):
        return min(score, 40)
    return score


def project_status_label(p: dict, notes: str) -> str:
    if not project_exists():
        return "Not Ready"
    if out_exists("final_report.md"):
        return "Ready for Presentation"
    if has_primary_outputs():
        return "Ready for Design"
    if data_sufficient(p, notes, pdfs_by_cat()):
        return "Ready for Analysis"
    if project_readiness(p, notes, list_pdfs()) > 0:
        return "Data Needed"
    return "Not Ready"


def readiness_hint(p: dict, notes: str, pdfs: list) -> str:
    st_label = project_status_label(p, notes)
    if st_label == "Ready for Presentation":
        return "可檢視成果並準備簡報。"
    if st_label == "Ready for Design":
        return "分析已完成，可進入設計與成果階段。"
    if st_label == "Ready for Analysis":
        return "資料已足夠，可啟動智慧分析。"
    if project_readiness(p, notes, pdfs) > 0:
        return "需要補充資料後才能進行可靠分析。"
    return "請先建立專案並填寫基本資料。"


def next_action_zh(p: dict, notes: str) -> str:
    if out_exists("final_report.md"):
        return "檢視簡報成果並匯出"
    if has_primary_outputs():
        return "檢視設計建議與決策摘要"
    overview = get_data_overview()
    pdf_n = overview["pdf_count"]
    link_n = overview["link_count"]
    if pdf_n == 0 and link_n == 0:
        return "請先至 Data Hub 新增 PDF 或網址資料來源"
    if pdf_n > 0 and link_n == 0:
        return "可補充政府公開資料或法規網址"
    if data_sufficient(p, notes, pdfs_by_cat()):
        return "啟動智慧分析"
    if empty(p.get("river_width")) or empty(p.get("soil_type")):
        return "補充工程與基地條件"
    if len(notes.strip()) < 30:
        return "撰寫知識筆記"
    return "完善專案資料"


def confidence_level(p: dict, notes: str) -> str:
    if not data_sufficient(p, notes, pdfs_by_cat()):
        return "Low"
    r = project_readiness(p, notes, list_pdfs())
    if r >= 70:
        return "High"
    if r >= 45:
        return "Medium"
    return "Low"


def decision_stage(p: dict, notes: str) -> str:
    if out_exists("final_report.md"):
        return "Presentation Ready"
    if has_primary_outputs():
        return "Concept Design"
    if data_sufficient(p, notes, pdfs_by_cat()):
        return "Preliminary"
    return "Not Ready" if project_readiness(p, notes, list_pdfs()) <= 15 else "Data Needed"


def extract_section(md: str, heading: str) -> str:
    pattern = rf"##\s*{re.escape(heading)}\s*\n(.*?)(?=\n##|\Z)"
    m = re.search(pattern, md, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def plain_preview(md: str, max_len: int = 380) -> str:
    if not md:
        return ""
    text = re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\n+", " ", text).strip()
    return text[:max_len] + ("…" if len(text) > max_len else "")


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def glass(html: str) -> None:
    st.markdown(f'<div class="glass">{html}</div>', unsafe_allow_html=True)


def mini_cell(label: str, value: str) -> str:
    v = value if value and value != "（未填寫）" else "尚未填寫"
    return f'<div class="mini-cell"><div class="k">{label}</div><div class="v">{v}</div></div>'


def pipeline_html(p: dict) -> str:
    done_map = {
        "research": out_exists("research_summary.md"),
        "engineering": out_exists("engineering_analysis.md"),
        "environment": out_exists("environmental_sustainability.md"),
        "design": out_exists("design_bim_visualization.md"),
        "ai": out_exists("ai_integration_plan.md"),
        "cost": out_exists("cost_schedule_analysis.md"),
        "report": out_exists("final_report.md"),
    }
    labels = ["Research", "Engineering", "Environment", "Design", "AI Strategy", "Cost", "Report"]
    keys = ["research", "engineering", "environment", "design", "ai", "cost", "report"]
    parts = []
    for label, key in zip(labels, keys):
        cls = "dot done" if done_map.get(key) else "dot"
        parts.append(f'<div class="p-step"><span class="{cls}"></span>{label}</div>')
    return f'<div class="pipeline">{"".join(parts)}</div>'


# ── Generators (Apple-style outputs) ─────────────────────────────────────────
def gen_recommendation(p: dict, notes: str, pdfs: dict, readiness: int) -> str:
    missing = missing_items(p, notes, pdfs)
    sufficient = data_sufficient(p, notes, pdfs)
    concepts = p.get("possible_design_concepts", [])
    rec = concepts[0] if sufficient and concepts else ""

    status = f"資料完整度約 {readiness}%。已上傳 {sum(len(v) for v in pdfs.values())} 份文件。"
    if sufficient:
        rec_block = f"""## Recommendation

建議優先評估：**{rec}**

## Key Reasons

- 符合專案目標：{p.get("bridge_type_goal", "")}
- 已具備基本工程與環境資料
- 可進入概念設計與 BIM 參數化階段

## Main Risks

{_bl(missing[:4]) if missing else "- 細部地質與發包風險仍需確認"}

## Next Actions

1. 確認推薦方案與團隊共識
2. 建立 BIM 構件清單
3. 準備簡報與決策材料
"""
    else:
        rec_block = f"""## Recommendation

目前資料不足，尚無法提出可靠橋型建議。

## Key Reasons

- 關鍵工程或環境資料尚未齊全
- 缺少足夠參考文件或筆記

## Main Risks

- 過早定案可能導致決策偏差

## Next Actions

{_bl(missing[:7])}
"""

    return f"""# BridgeMind Recommendation

## Current Status

- 專案：{p.get("project_name")}
- 位置：{p.get("location")}
- {status}

{rec_block}
"""


def gen_executive_summary(p: dict, notes: str, pdfs: dict, readiness: int) -> str:
    missing = missing_items(p, notes, pdfs)
    sufficient = data_sufficient(p, notes, pdfs)
    link_n = len(load_source_links())
    return f"""# Executive Summary

## Project

{p.get("project_name")} · {p.get("location")} · {p.get("bridge_type_goal")}

## Status

{"資料已足夠進行初步分析。" if sufficient else "資料尚不足，建議先補充關鍵資料。"}

## What We Know

- 已填寫之工程與專案欄位
- PDF 文件 {sum(len(v) for v in pdfs.values())} 份
- 網址資料 {link_n} 筆
- 知識筆記 {len(notes.strip())} 字

## What Is Missing

{_bl(missing[:6]) if missing else "- 無重大缺項"}

## Next Step

{next_action_zh(p, notes)}
"""


def gen_decision_dashboard(p: dict, notes: str, readiness: int) -> str:
    conf = confidence_level(p, notes)
    stage = decision_stage(p, notes)
    why = [
        f"專案準備度 {readiness}%，目前處於 {stage} 階段。",
        f"信心水準：{conf}。",
        readiness_hint(p, notes, list_pdfs()),
    ]
    return f"""# Decision Dashboard

## Project Readiness

{readiness}% — {project_status_label(p, notes)}

## Confidence

{conf}

## Decision Stage

{stage}

## Why

{chr(10).join(why)}
"""


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return ""
    sep = "| " + " | ".join(headers) + " |"
    line = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return f"{sep}\n{line}\n{body}"


def gen_research(p: dict, notes: str, pdfs: dict) -> str:
    missing = missing_items(p, notes, pdfs)
    links = load_source_links()
    docs = get_uploaded_documents()
    notes_len = len(notes.strip())

    if links:
        link_rows = [
            [lnk.get("title", ""), lnk.get("category", ""), lnk.get("url", ""), lnk.get("note", "") or "—"]
            for lnk in links
        ]
        links_block = "## 網址資料來源\n\n" + _md_table(["標題", "分類", "URL", "備註"], link_rows)
    else:
        links_block = "## 網址資料來源\n\n目前尚未新增任何網址資料來源。"

    if docs:
        pdf_rows = [[d["name"], d["category"], d["size_display"]] for d in docs]
        pdfs_block = "## PDF 文件來源\n\n" + _md_table(["文件名稱", "分類", "大小"], pdf_rows)
    else:
        pdfs_block = "## PDF 文件來源\n\n目前尚未上傳任何 PDF 文件。"

    notes_status = "有內容" if notes_len > 0 else "尚無內容"
    notes_block = f"""## 知識筆記狀態

- 字數：{notes_len}
- 是否有內容：{notes_status}
"""

    return f"""# 資料研究摘要

## 摘要

已盤點專案資料、{len(docs)} 份 PDF 與 {len(links)} 筆網址來源。

## 已有資料

- 專案：{p.get("project_name")}
- 河寬：{p.get("river_width") or "未填"}
- 地層：{p.get("soil_type") or "未填"}

{links_block}

{pdfs_block}

{notes_block}

## 缺少資料

{_bl(missing) if missing else "無"}
"""


def gen_engineering(p: dict, notes: str, pdfs: dict) -> str:
    if not has_basic_engineering(p):
        return f"""# 工程可行性分析

## 工程可行性摘要

資料不足，尚無法確認工程可行性。

## 下一步工程資料需求

{_bl(missing_items(p, notes, pdfs)[:6])}
"""
    return f"""# 工程可行性分析

## 工程可行性摘要

依現有河寬、地層與基礎資料，可進行**初步**工程討論。

## 重點

- 河寬：{p.get("river_width")}
- 地層：{p.get("soil_type")}
- 基礎：{p.get("foundation_method") or "待填"}

## 風險

軟弱地盤、防洪、施工交通 — 需進一步驗證。
"""


def gen_environmental(p: dict, notes: str, pdfs: dict) -> str:
    return f"""# 環境永續分析

## 環境影響摘要

濕地：{p.get("wetland") or "未填"}
環境限制：{len(p.get("environment_constraints", []))} 項

## 減輕對策

低衝擊施工、水質防制、生態監測

## 缺少資料

{"環評文件" if not pdfs.get("環評資料") else "已部分具備"}
"""


def gen_design(p: dict, notes: str, pdfs: dict) -> tuple[str, dict]:
    sufficient = data_sufficient(p, notes, pdfs)
    missing = missing_items(p, notes, pdfs)
    concepts = p.get("possible_design_concepts", [])
    rec = concepts[0] if sufficient and concepts else ""

    bim = {
        "recommended_concept": rec or None,
        "required_bim_components": p.get("bim_required_elements", []),
        "bridge_width_m": p.get("bridge_width_m"),
        "river_width": p.get("river_width"),
        "status": "ready" if sufficient else "insufficient",
    }

    if not sufficient:
        md = f"""# 設計與 BIM 規劃

目前資料不足，尚無法可靠推薦橋型。

請補充：河寬、橋長、地層、環評、交通需求與案例。

{_bl(missing[:8])}
"""
        return md, bim

    return f"""# 設計與 BIM 規劃

## 推薦概念

{rec}

## BIM 構件

{len(p.get("bim_required_elements", []))} 項已列出
""", bim


def gen_ai(p: dict) -> str:
    ai = p.get("ai_requirements", {})
    lines = []
    if ai.get("use_rag"):
        lines.append("- **文件檢索**：自動閱讀環評與法規重點")
    if ai.get("use_agentic_ai"):
        lines.append("- **多專業協作**：不同分析模組分工")
    if ai.get("use_cnn"):
        lines.append("- **影像辨識**：現場裂縫與施工監看")
    if ai.get("use_pinn"):
        lines.append("- **物理模擬**：加速結構與水文計算")
    if ai.get("use_digital_twin"):
        lines.append("- **數位孿生**：營運期監測維護")
    if ai.get("use_generative_ai"):
        lines.append("- **生成式設計**：橋型與視覺方案探索")
    body = "\n".join(lines) if lines else "- 尚未啟用 AI 方向（可於 Data → 進階設定勾選）"
    return f"""# AI 導入策略

## 白話說明

{body}
"""


def gen_cost(p: dict) -> str:
    if empty(p.get("bridge_length")) and empty(p.get("bridge_width_m")):
        return """# 經費與工期分析

## 摘要

缺少橋梁尺度與工法，尚無法估算。

## 缺少

橋長、橋型、工法、工期條件
"""
    return f"""# 經費與工期分析

## 摘要

可提出初步成本與工期**架構**，正式估算需設計深化。

## 工期架構

規劃 → 設計 → 施工 → 驗收
"""


def gen_final_report(p: dict, notes: str, pdfs: dict) -> tuple[str, str]:
    rec = p.get("possible_design_concepts", [""])[0] if data_sufficient(p, notes, pdfs) else "（待資料補齊）"
    final = f"""# {p.get("project_name")} — 最終報告

## 專案背景

{p.get("location")} · {p.get("bridge_type_goal")}

## 工程可行性

見工程分析章節。

## 環境永續

見環境分析章節。

## 設計建議

{rec}

## 結論

補齊資料後可進入概念設計與簡報階段。
"""
    ppt = f"""# 簡報大綱

| # | 內容 |
|---|------|
| 1 | 封面 — {p.get("project_name")} |
| 2 | 專案背景 |
| 3 | 現況與挑戰 |
| 4 | BridgeMind 方法 |
| 5 | 資料與研究 |
| 6 | 工程分析 |
| 7 | 環境永續 |
| 8 | 設計方向 |
| 9 | BIM |
| 10 | AI 導入 |
| 11 | 經費工期 |
| 12 | 推薦方案 |
| 13 | 創新價值 |
| 14 | 風險 |
| 15 | 結論 |
"""
    return final, ppt


def run_pipeline(p: dict, notes: str, cb: Callable | None = None) -> None:
    pdfs = pdfs_by_cat()
    readiness = project_readiness(p, notes, list_pdfs())

    steps: list[tuple[str, Callable[[], None]]] = [
        ("research", lambda: write_out("research_summary.md", gen_research(p, notes, pdfs))),
        ("engineering", lambda: write_out("engineering_analysis.md", gen_engineering(p, notes, pdfs))),
        ("environment", lambda: write_out("environmental_sustainability.md", gen_environmental(p, notes, pdfs))),
        ("design", lambda: _run_design(p, notes, pdfs)),
        ("ai", lambda: write_out("ai_integration_plan.md", gen_ai(p))),
        ("cost", lambda: write_out("cost_schedule_analysis.md", gen_cost(p))),
        ("report", lambda: _run_report(p, notes, pdfs)),
    ]
    for i, (key, fn) in enumerate(steps):
        if cb:
            cb(key, i, len(steps), "running")
        fn()
        if cb:
            cb(key, i, len(steps), "done")

    write_out("00_bridgemind_recommendation.md", gen_recommendation(p, notes, pdfs, readiness))
    write_out("01_executive_summary.md", gen_executive_summary(p, notes, pdfs, readiness))
    write_out("02_decision_dashboard.md", gen_decision_dashboard(p, notes, pdfs, readiness))


def _run_design(p: dict, notes: str, pdfs: dict) -> None:
    md, bim = gen_design(p, notes, pdfs)
    write_out("design_bim_visualization.md", md)
    write_out("bim_parameters.json", json.dumps(bim, ensure_ascii=False, indent=2))


def _run_report(p: dict, notes: str, pdfs: dict) -> None:
    f, ppt = gen_final_report(p, notes, pdfs)
    write_out("final_report.md", f)
    write_out("ppt_outline.md", ppt)


# ── UI: Onboarding ───────────────────────────────────────────────────────────
def page_onboarding() -> None:
    st.markdown('<p class="display">BridgeMind AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="subhead">智慧橋梁決策平台</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="glass-hero">'
        '<p class="display-sm" style="margin-bottom:0.75rem">尚未建立專案</p>'
        '<p class="subhead" style="max-width:420px;margin:0 auto">'
        "建立第一個橋梁專案，開始進行資料匯入、工程分析、BIM 規劃與決策輸出。"
        "</p></div>",
        unsafe_allow_html=True,
    )
    with st.form("create"):
        st.markdown('<p class="section-label">新專案</p>', unsafe_allow_html=True)
        name = st.text_input("專案名稱", placeholder="例如：河景觀橋")
        loc = st.text_input("專案位置", placeholder="例如：縣市・河段")
        goal = st.text_input("橋梁目標", placeholder="例如：景觀大橋")
        if st.form_submit_button("建立專案", type="primary", use_container_width=True):
            if not all([name.strip(), loc.strip(), goal.strip()]):
                st.error("請填寫三個欄位")
            else:
                create_project(name, loc, goal)
                st.rerun()


# ── UI: Project ────────────────────────────────────────────────────────────────
def page_project(p: dict) -> None:
    notes = load_notes()
    pdfs = list_pdfs()
    readiness = project_readiness(p, notes, pdfs)
    status = project_status_label(p, notes)
    pill_cls = "ready" if status.startswith("Ready") else ("warn" if status == "Data Needed" else "")

    st.markdown(f'<p class="display">{p.get("project_name")}</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="subhead">{p.get("bridge_type_goal")} · {p.get("location")}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<span class="status-pill {pill_cls}">{status}</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<div class="glass"><div class="readiness-label">Project Readiness</div>'
        f'<div class="readiness-num">{readiness}%</div>'
        f'<p class="subhead" style="margin-top:1rem">{readiness_hint(p, notes, pdfs)}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="glass-sm"><div class="readiness-label">下一步</div>'
        f'<p style="font-size:1.15rem;color:#F5F5F7;font-weight:500;margin:0.5rem 0 0">'
        f'{next_action_zh(p, notes)}</p></div>',
        unsafe_allow_html=True,
    )

    ov = get_data_overview()
    st.markdown('<p class="section-label">資料狀態</p>', unsafe_allow_html=True)
    cells = [
        mini_cell("PDF 文件", f"{ov['pdf_count']} 份"),
        mini_cell("網址資料", f"{ov['link_count']} 筆"),
        mini_cell("知識筆記", f"{ov['notes_length']} 字"),
        mini_cell("已涵蓋分類", f"{ov['categories_covered']} / {len(SOURCE_CATEGORIES)}"),
        mini_cell("資料完整度", f"{readiness}%"),
        mini_cell("分析成果", "已完成" if has_primary_outputs() else "尚未填寫"),
    ]
    st.markdown(f'<div class="mini-grid">{"".join(cells)}</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Snapshot</p>', unsafe_allow_html=True)
    snapshot_cells = [
        mini_cell("位置", p.get("location", "")),
        mini_cell("橋梁目標", p.get("bridge_type_goal", "")),
        mini_cell("BIM", "已就緒" if out_exists("bim_parameters.json") else "尚未填寫"),
    ]
    st.markdown(f'<div class="mini-grid">{"".join(snapshot_cells)}</div>', unsafe_allow_html=True)

    st.markdown(pipeline_html(p), unsafe_allow_html=True)


def _render_doc_popover_actions(doc: dict, idx: int) -> None:
    """單一文件：預覽、下載、刪除（含確認）。"""
    sk = _doc_session_key(doc)
    preview_key = f"doc_preview_{sk}"
    pending_key = f"doc_pending_delete_{sk}"

    popover_fn = getattr(st, "popover", None)
    container = popover_fn("⋯") if popover_fn else st.expander("⋯ 更多操作")

    with container:
        st.markdown('<p class="doc-action-label">更多操作</p>', unsafe_allow_html=True)

        if st.button("👁️ 預覽文件", key=f"btn_preview_{sk}", use_container_width=True):
            st.session_state[preview_key] = not st.session_state.get(preview_key, False)

        if st.session_state.get(preview_key):
            path = Path(doc["path"])
            exists = path.is_file()
            try:
                rel = path.relative_to(ROOT) if exists else doc["path"]
            except ValueError:
                rel = doc["path"]
            st.markdown(
                f'<div class="doc-preview-box">'
                f"<strong>文件名稱</strong><br>{html.escape(doc['name'])}<br><br>"
                f"<strong>文件分類</strong><br>{html.escape(doc['category'])}<br><br>"
                f"<strong>文件大小</strong><br>{html.escape(doc['size_display'])}<br><br>"
                f"<strong>文件路徑</strong><br>{html.escape(str(rel))}<br><br>"
                f"目前僅提供文件資訊預覽，PDF 內容解析將於 RAG 模組完成後支援。"
                f"</div>",
                unsafe_allow_html=True,
            )
            if not exists:
                st.caption("此檔案可能已被移動或刪除。")

        path = Path(doc["path"])
        if path.is_file():
            try:
                file_bytes = path.read_bytes()
                st.download_button(
                    label="下載文件",
                    data=file_bytes,
                    file_name=doc["name"],
                    mime="application/pdf",
                    key=f"dl_doc_{sk}",
                    use_container_width=True,
                )
            except OSError as e:
                st.caption(f"無法讀取檔案：{e}")
        else:
            st.caption("檔案不存在，無法下載。")

        if st.button("🗑️ 刪除文件", key=f"btn_del_req_{sk}", use_container_width=True):
            st.session_state[pending_key] = True

        if st.session_state.get(pending_key):
            st.markdown(
                '<p class="doc-delete-warn">確定要刪除此文件嗎？<br>此操作無法復原。</p>',
                unsafe_allow_html=True,
            )
            if st.button("確認刪除", key=f"btn_del_confirm_{sk}", use_container_width=True):
                success, msg = delete_document(doc["path"])
                if success:
                    st.session_state.pop(pending_key, None)
                    st.session_state.pop(preview_key, None)
                    st.success(f"已刪除文件：{doc['name']}")
                    st.rerun()
                else:
                    st.error(f"刪除失敗：{msg}")


def render_pdf_document_list() -> None:
    """PDF 文件清單（預覽、下載、刪除）。"""
    docs = get_uploaded_documents()

    st.markdown(
        '<div class="doc-list-header">'
        "<span>文件名稱</span><span>分類</span><span>大小</span><span>操作</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    if not docs:
        st.markdown(
            '<div class="glass-sm"><p class="subhead" style="margin:0">尚未上傳任何 PDF 文件。</p></div>',
            unsafe_allow_html=True,
        )
        return

    for idx, doc in enumerate(docs):
        safe_name = html.escape(doc["name"])
        safe_cat = html.escape(doc["category"])
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([5, 2, 1.2, 1])
            with c1:
                st.markdown(f'<div class="doc-name">{safe_name}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="doc-meta">{safe_cat}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(
                    f'<div class="doc-meta">{html.escape(doc["size_display"])}</div>',
                    unsafe_allow_html=True,
                )
            with c4:
                _render_doc_popover_actions(doc, idx)


def _render_link_actions(link: dict) -> None:
    lid = link.get("id", "")
    sk = hashlib.md5(lid.encode("utf-8")).hexdigest()[:12]
    pending_key = f"link_pending_delete_{sk}"
    popover_fn = getattr(st, "popover", None)
    container = popover_fn("⋯") if popover_fn else st.expander("⋯ 更多操作")
    with container:
        st.markdown('<p class="doc-action-label">更多操作</p>', unsafe_allow_html=True)
        st.markdown(f"[開啟網址]({link.get('url', '')})")
        if st.button("🗑️ 刪除網址", key=f"link_del_req_{sk}", use_container_width=True):
            st.session_state[pending_key] = True
        if st.session_state.get(pending_key):
            st.markdown(
                '<p class="doc-delete-warn">確定要刪除此網址嗎？<br>此操作無法復原。</p>',
                unsafe_allow_html=True,
            )
            if st.button("確認刪除", key=f"link_del_confirm_{sk}", use_container_width=True):
                ok, msg = delete_source_link(lid)
                if ok:
                    st.session_state.pop(pending_key, None)
                    st.success(f"已刪除：{link.get('title', '')}")
                    st.rerun()
                else:
                    st.error(f"刪除失敗：{msg}")


def tab_pdf_documents() -> None:
    st.markdown('<p class="hub-tab-title">PDF 文件庫</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hub-tab-desc">上傳環評、可行性評估、橋梁案例與法規等 PDF 文件。</p>',
        unsafe_allow_html=True,
    )
    cat = st.selectbox("分類", SOURCE_CATEGORIES, key="pdf_upload_category")
    files = st.file_uploader(
        "上傳 PDF 文件",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader",
    )
    if st.button("儲存 PDF 文件", type="primary", key="save_pdfs") and files:
        folder = category_folder_path(cat)
        saved = 0
        for f in files:
            dest = get_unique_filepath(folder, f.name)
            dest.write_bytes(f.getvalue())
            saved += 1
        st.success(f"已儲存 {saved} 份 PDF 至「{cat}」")
        st.rerun()

    st.markdown('<p class="section-label" style="margin-top:1.5rem">文件清單</p>', unsafe_allow_html=True)
    render_pdf_document_list()


def tab_source_links() -> None:
    st.markdown('<p class="hub-tab-title">網址資料庫</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hub-tab-desc">新增政府資料、橋梁案例、法規、BIM 或 AI 技術相關網址。</p>',
        unsafe_allow_html=True,
    )
    with st.form("add_link_form"):
        title = st.text_input("資料標題", placeholder="例如：政府資料開放平臺 — 橋梁統計")
        url = st.text_input("網址 URL", placeholder="https://...")
        cat = st.selectbox("分類", SOURCE_CATEGORIES, key="link_form_category")
        note = st.text_area("備註", height=80, placeholder="選填：資料用途或重點")
        submitted = st.form_submit_button("儲存網址", type="primary")
        if submitted:
            ok, msg = add_source_link(title, url, cat, note)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    links = load_source_links()
    st.markdown('<p class="section-label" style="margin-top:1.5rem">網址清單</p>', unsafe_allow_html=True)
    if not links:
        st.markdown(
            '<div class="glass-sm"><p class="subhead" style="margin:0">尚未新增任何網址資料來源。</p></div>',
            unsafe_allow_html=True,
        )
        return

    for link in sorted(links, key=lambda x: x.get("created_at", ""), reverse=True):
        safe_title = html.escape(link.get("title", ""))
        safe_cat = html.escape(link.get("category", ""))
        safe_note = html.escape(link.get("note", "") or "—")
        safe_time = html.escape(link.get("created_at", ""))
        safe_url = html.escape(link.get("url", ""))
        with st.container(border=True):
            c1, c2 = st.columns([6, 1])
            with c1:
                st.markdown(
                    f'<div class="doc-name">{safe_title}</div>'
                    f'<div class="doc-meta">{safe_cat} · {safe_time}</div>'
                    f'<div class="link-url">{safe_url}</div>'
                    f'<div class="doc-meta" style="margin-top:0.35rem">備註：{safe_note}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"[開啟網址]({link.get('url', '')})")
            with c2:
                _render_link_actions(link)


def tab_knowledge_notes() -> None:
    st.markdown('<p class="hub-tab-title">知識筆記</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hub-tab-desc">貼上組員整理的工程資料、老師要求、橋梁設計內容或環評重點。</p>',
        unsafe_allow_html=True,
    )
    notes = load_notes()
    text = st.text_area(
        "知識筆記內容",
        notes,
        height=350,
        placeholder="貼上或輸入知識筆記…",
        label_visibility="collapsed",
        key="knowledge_notes_area",
    )
    char_count = len(text)
    st.markdown(f'<p class="caption">目前字數：{char_count}</p>', unsafe_allow_html=True)
    if not text.strip():
        st.markdown('<p class="caption">目前尚未建立知識筆記。</p>', unsafe_allow_html=True)
    if st.button("儲存知識筆記", type="primary", key="save_knowledge_notes"):
        save_notes(text)
        st.success("知識筆記已儲存")
        st.rerun()
    if text.strip():
        st.markdown('<p class="section-label">Markdown 預覽</p>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(text)


def tab_data_overview() -> None:
    st.markdown('<p class="hub-tab-title">資料總覽</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hub-tab-desc">檢視 PDF、網址與知識筆記的整體狀態與分類分布。</p>',
        unsafe_allow_html=True,
    )
    ov = get_data_overview()
    st.markdown(
        f'<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="n">{ov["pdf_count"]}</div><div class="l">PDF 文件</div></div>'
        f'<div class="kpi-card"><div class="n">{ov["link_count"]}</div><div class="l">網址資料</div></div>'
        f'<div class="kpi-card"><div class="n">{ov["notes_length"]}</div><div class="l">筆記字數</div></div>'
        f'<div class="kpi-card"><div class="n">{ov["categories_covered"]}</div><div class="l">已涵蓋分類</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-label">分類統計</p>', unsafe_allow_html=True)
    rows = []
    for cat in SOURCE_CATEGORIES:
        pdf_n = ov["pdf_by_cat"].get(cat, 0)
        link_n = ov["link_by_cat"].get(cat, 0)
        if pdf_n > 0 or link_n > 0:
            rows.append({"分類": cat, "PDF": pdf_n, "網址": link_n})
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="caption">尚無任何分類資料。</p>', unsafe_allow_html=True)

    if ov["core_gaps"]:
        st.markdown('<p class="section-label">資料完整度提示</p>', unsafe_allow_html=True)
        for hint in ov["core_gaps"]:
            st.markdown(f'<div class="warn-hint">{html.escape(hint)}</div>', unsafe_allow_html=True)

    completeness = calculate_data_completeness(
        load_profile() or {},
        load_notes(),
        list_pdfs(),
        load_source_links(),
    )
    st.markdown(
        f'<div class="glass-sm" style="margin-top:1rem">'
        f'<p class="caption" style="margin:0">資料完整度（profile / 筆記 / PDF / 網址）</p>'
        f'<p style="font-size:1.5rem;font-weight:600;color:#F5F5F7;margin:0.35rem 0 0">{completeness}%</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


# ── UI: Data ─────────────────────────────────────────────────────────────────
def page_data(p: dict) -> None:
    st.markdown('<p class="display-sm">Data Hub</p>', unsafe_allow_html=True)
    st.markdown('<p class="subhead">資料中心</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption" style="margin-top:0.5rem">'
        "集中管理 PDF 文件、網址資料與知識筆記，作為 BridgeMind AI 分析基礎。"
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    tab_pdf, tab_url, tab_notes, tab_overview = st.tabs(
        ["PDF 文件", "網址資料", "知識筆記", "資料總覽"]
    )
    with tab_pdf:
        tab_pdf_documents()
    with tab_url:
        tab_source_links()
    with tab_notes:
        tab_knowledge_notes()
    with tab_overview:
        tab_data_overview()

    st.markdown('<p class="section-label">Project Basics</p>', unsafe_allow_html=True)
    with st.form("basics"):
        c1, c2 = st.columns(2)
        pn = c1.text_input("專案名稱", p.get("project_name", ""))
        loc = c2.text_input("專案位置", p.get("location", ""))
        goal = c1.text_input("橋梁目標", p.get("bridge_type_goal", ""))
        rw = c2.text_input("河寬", p.get("river_width", ""))
        blen = c1.text_input("橋梁全長", p.get("bridge_length", ""))
        bw = c2.text_input("橋面寬度", str(p.get("bridge_width_m") or ""))
        spd = c1.text_input("設計速率", str(p.get("design_speed_kmh") or ""))
        soil = c2.text_input("地層條件", p.get("soil_type", ""))
        if st.form_submit_button("儲存專案資料", type="primary"):
            p.update({
                "project_name": pn, "location": loc, "bridge_type_goal": goal,
                "river_width": rw, "bridge_length": blen, "bridge_width_m": bw,
                "design_speed_kmh": spd, "soil_type": soil,
            })
            save_profile(p)
            st.rerun()

    with st.expander("Advanced Details"):
        with st.form("adv"):
            found = st.text_input("基礎工法", p.get("foundation_method", ""))
            route = st.text_area("路線策略", list_to_lines(p.get("route_strategy")))
            eng = st.text_area("工程限制", list_to_lines(p.get("engineering_constraints")))
            types = st.text_area("橋型候選", list_to_lines(p.get("bridge_type_candidates")))
            wet = st.text_input("濕地條件", p.get("wetland", ""))
            env = st.text_area("環境限制", list_to_lines(p.get("environment_constraints")))
            kw = st.text_area("設計關鍵字", list_to_lines(p.get("design_keywords")))
            concepts = st.text_area("橋梁概念", list_to_lines(p.get("possible_design_concepts")))
            bim = st.text_area("BIM 構件", list_to_lines(p.get("bim_required_elements")))
            ai = p.get("ai_requirements", {})
            c1, c2, c3 = st.columns(3)
            u = {
                "use_rag": c1.checkbox("RAG", ai.get("use_rag", False)),
                "use_cnn": c2.checkbox("CNN", ai.get("use_cnn", False)),
                "use_pinn": c3.checkbox("PINN", ai.get("use_pinn", False)),
                "use_agentic_ai": c1.checkbox("Agentic AI", ai.get("use_agentic_ai", False)),
                "use_digital_twin": c2.checkbox("Digital Twin", ai.get("use_digital_twin", False)),
                "use_generative_ai": c3.checkbox("Generative AI", ai.get("use_generative_ai", False)),
            }
            if st.form_submit_button("儲存進階設定"):
                p.update({
                    "foundation_method": found, "route_strategy": lines_to_list(route),
                    "engineering_constraints": lines_to_list(eng),
                    "bridge_type_candidates": lines_to_list(types),
                    "wetland": wet, "environment_constraints": lines_to_list(env),
                    "design_keywords": lines_to_list(kw),
                    "possible_design_concepts": lines_to_list(concepts),
                    "bim_required_elements": lines_to_list(bim),
                    "ai_requirements": u,
                })
                save_profile(p)
                st.rerun()


# ── UI: Analysis ───────────────────────────────────────────────────────────────
def page_analysis(p: dict) -> None:
    st.markdown('<p class="display-sm">AI Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="subhead">將資料轉換為工程判斷、設計方向與決策建議</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("啟動智慧分析", type="primary", use_container_width=True):
        notes = load_notes()
        prog = st.progress(0)
        status = st.empty()
        state = st.session_state.get("pipe", {})

        def cb(key, idx, total, phase):
            state[key] = phase
            st.session_state.pipe = state
            prog.progress((idx + (0.5 if phase == "running" else 1)) / total)

        with st.spinner("分析中…"):
            run_pipeline(p, notes, cb)
        status.success("分析完成")
        st.rerun()

    st.markdown(pipeline_html(p), unsafe_allow_html=True)

    if not has_primary_outputs():
        st.markdown(
            '<div class="glass-sm"><p class="subhead" style="margin:0">'
            "尚未執行分析。請先輸入資料後啟動智慧分析。"
            "</p></div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown('<p class="section-label">Results</p>', unsafe_allow_html=True)

    rec = read_out("00_bridgemind_recommendation.md")
    if rec:
        preview = plain_preview(extract_section(rec, "Recommendation") or extract_section(rec, "Current Status") or rec)
        st.markdown(
            f'<div class="glass"><p class="package-title">Decision Brief</p>'
            f'<p class="card-preview">{preview}</p></div>',
            unsafe_allow_html=True,
        )
        with st.expander("閱讀完整決策建議"):
            st.markdown(rec)

    exe = read_out("01_executive_summary.md")
    if exe:
        preview = plain_preview(extract_section(exe, "Next Step") or exe, 280)
        st.markdown(
            f'<div class="glass"><p class="package-title">Executive Summary</p>'
            f'<p class="card-preview">{preview}</p></div>',
            unsafe_allow_html=True,
        )
        with st.expander("閱讀完整主管摘要"):
            st.markdown(exe)

    with st.expander("Technical Reports"):
        for fname, title in TECH.items():
            if fname.endswith(".json"):
                continue
            c = read_out(fname)
            if c:
                st.markdown(f"**{title}**")
                st.markdown(c[:3000] + ("…" if len(c) > 3000 else ""))


# ── UI: Output ─────────────────────────────────────────────────────────────────
def _download_btn(label: str, fname: str, col) -> None:
    if out_exists(fname):
        col.download_button(label, (OUT / fname).read_text(encoding="utf-8"), fname, key=f"dl_{fname}", use_container_width=True)


def page_output(p: dict) -> None:
    st.markdown('<p class="display-sm">Output</p>', unsafe_allow_html=True)
    st.markdown('<p class="subhead">決策成果與交付物</p>', unsafe_allow_html=True)

    if not has_primary_outputs():
        st.markdown(
            '<div class="glass"><p class="subhead" style="margin:0">'
            "尚未產生成果，請先至 Analysis 啟動智慧分析。"
            "</p></div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown('<p class="section-label">Decision Package</p>', unsafe_allow_html=True)
    for fname, (dl_label, card_title) in PRIMARY.items():
        content = read_out(fname)
        if content:
            st.markdown(f'<div class="glass-sm"><p class="package-title">{card_title}</p></div>', unsafe_allow_html=True)
            with st.expander(f"預覽 · {card_title}"):
                st.markdown(content)
    c1, c2, c3 = st.columns(3)
    _download_btn("下載決策建議書", "00_bridgemind_recommendation.md", c1)
    _download_btn("下載主管摘要", "01_executive_summary.md", c2)
    _download_btn("下載決策儀表板", "02_decision_dashboard.md", c3)

    st.markdown('<p class="section-label">Technical Package</p>', unsafe_allow_html=True)
    tech_files = [k for k in TECH if not k.endswith(".json")]
    c1, c2, c3 = st.columns(3)
    for i, fname in enumerate(tech_files):
        if out_exists(fname):
            _download_btn(f"下載{TECH[fname]}", fname, [c1, c2, c3][i % 3])

    st.markdown('<p class="section-label">BIM Package</p>', unsafe_allow_html=True)
    if out_exists("bim_parameters.json"):
        with st.expander("BIM 參數預覽"):
            st.json(read_json_out("bim_parameters.json"))
        st.download_button(
            "下載 BIM 參數",
            (OUT / "bim_parameters.json").read_text(encoding="utf-8"),
            "bim_parameters.json",
            key="dl_bim",
        )
    else:
        st.markdown('<p class="caption">尚未產生 BIM 參數。</p>', unsafe_allow_html=True)

    if out_exists("design_bim_visualization.md"):
        with st.expander("設計與 BIM 規劃"):
            st.markdown(read_out("design_bim_visualization.md"))

    st.markdown('<p class="section-label">Presentation Package</p>', unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    _download_btn("下載最終報告", "final_report.md", p1)
    _download_btn("下載簡報大綱", "ppt_outline.md", p2)
    if not out_exists("final_report.md") and not out_exists("ppt_outline.md"):
        st.markdown('<p class="caption">尚未產生簡報成果。</p>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    if s1.button("清除分析成果", use_container_width=True):
        for f in OUT.iterdir():
            if f.is_file():
                f.unlink()
        st.session_state.pipe = {}
        st.rerun()
    if s2.button("重設專案", use_container_width=True):
        if PROFILE_PATH.exists():
            PROFILE_PATH.unlink()
        st.rerun()


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title="BridgeMind AI", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
    inject_css()
    ensure_dirs()

    if "page" not in st.session_state:
        st.session_state.page = "project"
    if "pipe" not in st.session_state:
        st.session_state.pipe = {}

    with st.sidebar:
        st.markdown('<p class="nav-brand">BridgeMind AI</p>', unsafe_allow_html=True)
        st.markdown('<p class="nav-sub">智慧橋梁決策平台</p>', unsafe_allow_html=True)
        for key, label in PAGES:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
        st.markdown(
            '<p class="sbf">Prototype v1.0<br>7-Agent Backend</p>',
            unsafe_allow_html=True,
        )

    if not project_exists():
        page_onboarding()
        return

    p = load_profile()
    if p is None:
        page_onboarding()
        return

    pages = {
        "project": lambda: page_project(p),
        "data": lambda: page_data(p),
        "analysis": lambda: page_analysis(p),
        "output": lambda: page_output(p),
    }
    pages[st.session_state.page]()


if __name__ == "__main__":
    main()
