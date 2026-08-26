"""Runtime configuration with privacy-safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_: object, **__: object) -> bool:
        return False


TRUE_VALUES = {"1", "true", "yes", "on"}


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings loaded from environment variables."""

    root_dir: Path
    data_dir: Path
    database_path: Path
    openai_api_key: str | None
    openai_model: str
    transcribe_model: str
    allow_cloud_memory_context: bool
    default_conversation_id: str
    timezone: str

    @classmethod
    def from_env(cls, root_dir: Path | None = None) -> "Settings":
        load_dotenv()
        resolved_root = (root_dir or Path(__file__).resolve().parent.parent).resolve()
        configured_data_dir = Path(os.getenv("FOUNDER_AI_DATA_DIR", ".local"))
        if not configured_data_dir.is_absolute():
            configured_data_dir = resolved_root / configured_data_dir
        data_dir = configured_data_dir.resolve()
        data_dir.mkdir(parents=True, exist_ok=True)

        raw_key = os.getenv("OPENAI_API_KEY", "").strip()
        return cls(
            root_dir=resolved_root,
            data_dir=data_dir,
            database_path=data_dir / "founder_company_ai.sqlite3",
            openai_api_key=raw_key or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5").strip() or "gpt-5",
            transcribe_model=(
                os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe").strip()
                or "gpt-4o-mini-transcribe"
            ),
            allow_cloud_memory_context=_as_bool(
                os.getenv("FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT"), default=False
            ),
            default_conversation_id=(
                os.getenv("FOUNDER_AI_DEFAULT_CONVERSATION_ID", "founder-main").strip()
                or "founder-main"
            ),
            timezone=os.getenv("FOUNDER_AI_TIMEZONE", "Asia/Taipei").strip() or "Asia/Taipei",
        )
