"""Global project settings and path configuration."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCUMENTS_DIR = DATA_DIR / "raw_documents"
PROCESSED_TEXT_DIR = DATA_DIR / "processed_text"
BRIDGE_INPUTS_DIR = DATA_DIR / "bridge_inputs"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
EXPORTS_DIR = PROJECT_ROOT / "exports"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

RAW_DOCUMENT_CATEGORIES = (
    "environmental_reports",
    "feasibility_reports",
    "bridge_cases",
    "regulations",
)

BRIDGE_PROFILE_FILE = BRIDGE_INPUTS_DIR / "zengwen_bridge_profile.json"
KNOWLEDGE_NOTES_FILE = KNOWLEDGE_BASE_DIR / "zengwen_bridge_notes.md"
RESEARCH_OUTPUT_FILE = OUTPUTS_DIR / "research_summary.md"
