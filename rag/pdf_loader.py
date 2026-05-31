"""PDF scanning and text extraction for the research pipeline."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PdfDocument:
    path: Path
    category: str
    text: str
    page_count: int
    extraction_error: str | None = None


def scan_pdf_files(raw_documents_dir: Path) -> list[Path]:
    return sorted(raw_documents_dir.rglob("*.pdf"))


def _category_for_pdf(raw_documents_dir: Path, pdf_path: Path) -> str:
    try:
        relative = pdf_path.relative_to(raw_documents_dir)
        if relative.parts:
            return relative.parts[0]
    except ValueError:
        pass
    return "uncategorized"


def extract_text_from_pdf(pdf_path: Path) -> tuple[str, int, str | None]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return "", 0, "pypdf is not installed"

    try:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())
        return "\n\n".join(pages), len(reader.pages), None
    except Exception as exc:
        return "", 0, str(exc)


def load_pdf_documents(raw_documents_dir: Path) -> list[PdfDocument]:
    documents: list[PdfDocument] = []
    for pdf_path in scan_pdf_files(raw_documents_dir):
        text, page_count, error = extract_text_from_pdf(pdf_path)
        documents.append(
            PdfDocument(
                path=pdf_path,
                category=_category_for_pdf(raw_documents_dir, pdf_path),
                text=text,
                page_count=page_count,
                extraction_error=error,
            )
        )
    return documents
