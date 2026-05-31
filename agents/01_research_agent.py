"""
Research Agent (01)

Collects project inputs, scans raw PDF documents, and produces a structured
research summary for downstream agents.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    BRIDGE_PROFILE_FILE,
    KNOWLEDGE_NOTES_FILE,
    RAW_DOCUMENTS_DIR,
    RAW_DOCUMENT_CATEGORIES,
    RESEARCH_OUTPUT_FILE,
)
from rag.pdf_loader import PdfDocument, load_pdf_documents, scan_pdf_files
from utils.file_utils import file_exists_and_nonempty, read_text, write_text
from utils.json_utils import load_json
from utils.markdown_utils import generation_header, md_heading

AGENT_NAME = "Research Agent (01)"

ENGINEERING_KEYWORD_SEEDS = (
    "alignment",
    "bridge length",
    "bridge type",
    "cast-in-place pile",
    "construction feasibility",
    "cross-section",
    "design speed",
    "detention",
    "drainage",
    "durability",
    "flood control",
    "foundation",
    "full-casing pile",
    "geotechnical",
    "girder",
    "horizontal alignment",
    "lane configuration",
    "main bridge",
    "motorcycle lane",
    "pile foundation",
    "route planning",
    "scour",
    "seismic",
    "soil",
    "span",
    "structural engineering",
    "traffic maintenance",
    "vertical alignment",
)

ENVIRONMENTAL_KEYWORD_SEEDS = (
    "air pollution",
    "black-faced spoonbill",
    "construction dust",
    "ecological restoration",
    "environment constraint",
    "environmental impact assessment",
    "estuary",
    "habitat",
    "low-impact development",
    "native planting",
    "noise",
    "overland flow",
    "purification trench",
    "sdg",
    "sustainability",
    "vibration",
    "water quality",
    "wetland",
    "wildlife corridor",
)

BIM_KEYWORD_SEEDS = (
    "abutment",
    "anti-unseating device",
    "bearing",
    "bim component",
    "bim parameter",
    "bridge deck",
    "bridge tower",
    "civil 3d",
    "digital twin",
    "drainage system",
    "expansion joint",
    "generative ai",
    "guardrail",
    "ifc",
    "landscape planting",
    "lighting system",
    "modeling workflow",
    "parameter table",
    "revit",
    "sketchup",
    "stay cable",
    "visualization",
)


@dataclass
class ResearchInputs:
    profile: dict
    notes: str
    notes_available: bool
    pdf_documents: list[PdfDocument] = field(default_factory=list)
    pdf_paths: list[Path] = field(default_factory=list)


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def _profile_to_text(profile: dict) -> str:
    parts: list[str] = []
    for key, value in profile.items():
        parts.append(f"{key}: {_normalize_text(value)}")
    return "\n".join(parts)


def _profile_values_text(profile: dict) -> str:
    values: list[str] = []
    for value in profile.values():
        text = _normalize_text(value).strip()
        if text:
            values.append(text)
    return "\n".join(values)


def _collect_corpus(inputs: ResearchInputs) -> str:
    chunks = [_profile_values_text(inputs.profile)]
    if inputs.notes_available:
        chunks.append(inputs.notes)
    for document in inputs.pdf_documents:
        if document.text:
            chunks.append(document.text)
    return "\n".join(chunks)


def _find_keywords(corpus: str, seeds: tuple[str, ...]) -> list[str]:
    corpus_lower = corpus.lower()
    found = [seed for seed in seeds if seed in corpus_lower]

    for token in re.findall(r"[A-Za-z][A-Za-z0-9\-/ ]{2,}", corpus):
        normalized = token.strip().lower()
        if len(normalized) < 4:
            continue
        if any(normalized in seed or seed in normalized for seed in seeds):
            if normalized not in found:
                found.append(normalized)

    return sorted(set(found), key=str.lower)


def _missing_profile_fields(profile: dict) -> list[str]:
    missing: list[str] = []
    for key, value in profile.items():
        if isinstance(value, list) and not value:
            missing.append(key)
        elif isinstance(value, str) and not value.strip():
            missing.append(key)
        elif value in (None, ""):
            missing.append(key)
    return missing


def _default_project_background(profile: dict) -> str:
    project_name = profile.get("project_name") or "Zengwen River Landscape Bridge"
    return (
        f"**{project_name}** is the target project for BridgeMind AI, an Agentic AI + BIM "
        "smart bridge design system developed for the Zengwen River Landscape Bridge competition.\n\n"
        "The Research Agent organizes available project inputs and identifies data gaps before "
        "engineering, environmental, design, AI integration, cost, and reporting agents run."
    )


def _format_profile_summary(profile: dict) -> list[str]:
    lines: list[str] = []
    for key, value in profile.items():
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value) if value else "_empty_"
        else:
            rendered = str(value).strip() if str(value).strip() else "_empty_"
        lines.append(f"- `{key}`: {rendered}")
    return lines


def _format_pdf_inventory(inputs: ResearchInputs) -> list[str]:
    if not inputs.pdf_paths:
        return ["- No PDF files found under `data/raw_documents/`."]

    lines: list[str] = []
    for pdf_path in inputs.pdf_paths:
        category = pdf_path.relative_to(RAW_DOCUMENTS_DIR).parts[0]
        lines.append(f"- `{pdf_path.relative_to(RAW_DOCUMENTS_DIR)}` ({category})")
    return lines


def _format_pdf_summaries(inputs: ResearchInputs) -> list[str]:
    if not inputs.pdf_documents:
        return []

    lines = [md_heading("PDF Document Summaries", level=3)]
    for document in inputs.pdf_documents:
        relative_path = document.path.relative_to(RAW_DOCUMENTS_DIR)
        lines.append(f"### `{relative_path}`\n")
        lines.append(f"- Category: `{document.category}`")
        lines.append(f"- Pages: {document.page_count}")

        if document.extraction_error:
            lines.append(f"- Extraction status: failed ({document.extraction_error})")
        elif document.text:
            preview = document.text[:500].replace("\n", " ").strip()
            lines.append(f"- Extraction status: success")
            lines.append(f"- Preview: {preview}...")
        else:
            lines.append("- Extraction status: no extractable text")

        lines.append("")
    return lines


def _missing_pdf_categories(inputs: ResearchInputs) -> list[str]:
    present = {document.category for document in inputs.pdf_documents}
    return [category for category in RAW_DOCUMENT_CATEGORIES if category not in present]


def _recommended_tasks(inputs: ResearchInputs, missing_profile: list[str]) -> list[str]:
    tasks: list[str] = []

    if missing_profile:
        tasks.append(
            "Complete `data/bridge_inputs/zengwen_bridge_profile.json` with project name, "
            "river width, wetland context, soil type, bridge length, and environment constraints."
        )

    if not inputs.notes_available:
        tasks.append(
            "Populate `data/knowledge_base/zengwen_bridge_notes.md` with site notes, "
            "design assumptions, and competition requirements."
        )

    for category in _missing_pdf_categories(inputs):
        tasks.append(f"Add PDF files to `data/raw_documents/{category}/`.")

    if inputs.pdf_documents and any(not doc.text for doc in inputs.pdf_documents):
        tasks.append(
            "Review PDFs with failed or empty text extraction; provide searchable copies "
            "or add key excerpts to the knowledge base notes."
        )

    if not tasks:
        tasks.append(
            "Review the generated keyword lists and confirm that engineering, environmental, "
            "and BIM terminology coverage is sufficient for downstream agents."
        )

    return tasks


def load_inputs(
    profile_path: Path | None = None,
    notes_path: Path | None = None,
    raw_documents_dir: Path | None = None,
) -> ResearchInputs:
    profile_file = profile_path or BRIDGE_PROFILE_FILE
    notes_file = notes_path or KNOWLEDGE_NOTES_FILE
    documents_dir = raw_documents_dir or RAW_DOCUMENTS_DIR

    profile = load_json(profile_file) if profile_file.exists() else {}
    notes_available = file_exists_and_nonempty(notes_file)
    notes = read_text(notes_file) if notes_available else ""
    pdf_paths = scan_pdf_files(documents_dir)
    pdf_documents = load_pdf_documents(documents_dir)

    return ResearchInputs(
        profile=profile,
        notes=notes,
        notes_available=notes_available,
        pdf_documents=pdf_documents,
        pdf_paths=pdf_paths,
    )


def build_research_summary(inputs: ResearchInputs) -> str:
    corpus = _collect_corpus(inputs)
    missing_profile = _missing_profile_fields(inputs.profile)
    engineering_keywords = _find_keywords(corpus, ENGINEERING_KEYWORD_SEEDS)
    environmental_keywords = _find_keywords(corpus, ENVIRONMENTAL_KEYWORD_SEEDS)
    bim_keywords = _find_keywords(corpus, BIM_KEYWORD_SEEDS)

    sections: list[str] = [generation_header(AGENT_NAME), md_heading("Research Summary", level=1)]

    sections.append(md_heading("Project Background"))
    sections.append(_default_project_background(inputs.profile))
    sections.append("\n\n")

    sections.append(md_heading("Available Data"))
    sections.append("### Bridge Profile\n")
    sections.extend(line + "\n" for line in _format_profile_summary(inputs.profile))
    sections.append("\n### Knowledge Base Notes\n")
    if inputs.notes_available:
        sections.append("Notes file loaded from `data/knowledge_base/zengwen_bridge_notes.md`.\n\n")
        sections.append(inputs.notes.strip())
        sections.append("\n\n")
    else:
        sections.append("- Knowledge base notes file is missing or empty.\n\n")

    sections.append("### Raw PDF Documents\n")
    sections.extend(line + "\n" for line in _format_pdf_inventory(inputs))
    sections.append("\n")
    sections.extend(_format_pdf_summaries(inputs))

    sections.append(md_heading("Missing Data"))
    missing_lines: list[str] = []
    if missing_profile:
        missing_lines.append(
            "- Empty bridge profile fields: "
            + ", ".join(f"`{field}`" for field in missing_profile)
        )
    else:
        missing_lines.append("- Bridge profile fields are populated.")

    if not inputs.notes_available:
        missing_lines.append("- Knowledge base notes are unavailable.")

    if not inputs.pdf_paths:
        missing_lines.append("- No PDF documents are available in `data/raw_documents/`.")

    missing_categories = _missing_pdf_categories(inputs)
    if missing_categories:
        missing_lines.append(
            "- Missing PDF categories: "
            + ", ".join(f"`{category}`" for category in missing_categories)
        )

    sections.extend(line + "\n" for line in missing_lines)
    sections.append("\n")

    sections.append(md_heading("Engineering Keywords"))
    if engineering_keywords:
        sections.append(", ".join(f"`{keyword}`" for keyword in engineering_keywords))
    else:
        sections.append("_No engineering keywords detected yet. Add profile data, notes, or PDFs._")
    sections.append("\n\n")

    sections.append(md_heading("Environmental Keywords"))
    if environmental_keywords:
        sections.append(", ".join(f"`{keyword}`" for keyword in environmental_keywords))
    else:
        sections.append(
            "_No environmental keywords detected yet. Add wetland, ecology, or EIA-related inputs._"
        )
    sections.append("\n\n")

    sections.append(md_heading("BIM-Related Keywords"))
    if bim_keywords:
        sections.append(", ".join(f"`{keyword}`" for keyword in bim_keywords))
    else:
        sections.append(
            "_No BIM-related keywords detected yet. Add design notes or BIM reference documents._"
        )
    sections.append("\n\n")

    sections.append(md_heading("Recommended Next Data Collection Tasks"))
    for index, task in enumerate(_recommended_tasks(inputs, missing_profile), start=1):
        sections.append(f"{index}. {task}\n")

    return "".join(sections).rstrip() + "\n"


def run(
    profile_path: Path | None = None,
    notes_path: Path | None = None,
    raw_documents_dir: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    inputs = load_inputs(profile_path, notes_path, raw_documents_dir)
    summary = build_research_summary(inputs)
    target = output_path or RESEARCH_OUTPUT_FILE
    write_text(target, summary)
    return target


if __name__ == "__main__":
    output = run()
    print(f"Research summary saved to: {output}")
