"""Provider protocol."""

from __future__ import annotations

from typing import Protocol, Sequence

from founder_company_ai.models import MessageRecord


class AIProvider(Protocol):
    def reply(self, *, system_prompt: str, messages: Sequence[MessageRecord]) -> str:
        ...

    def transcribe(self, *, audio_bytes: bytes, filename: str = "voice.wav") -> str:
        ...
