"""OpenAI Responses API and transcription adapter."""

from __future__ import annotations

import io
from typing import Sequence

from founder_company_ai.models import MessageRecord


class OpenAIProvider:
    """Thin boundary that keeps the product replaceable and permission-aware."""

    def __init__(self, *, api_key: str, model: str, transcribe_model: str):
        if not api_key.strip():
            raise ValueError("An API key is required.")
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("The openai package is not installed.") from exc

        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.transcribe_model = transcribe_model

    def reply(self, *, system_prompt: str, messages: Sequence[MessageRecord]) -> str:
        response = self._client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages[-20:]
            ],
            store=False,
        )
        output_text = getattr(response, "output_text", "")
        if not output_text or not output_text.strip():
            raise RuntimeError("The AI provider returned an empty response.")
        return output_text.strip()

    def transcribe(self, *, audio_bytes: bytes, filename: str = "voice.wav") -> str:
        if not audio_bytes:
            raise ValueError("Audio is empty.")
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename or "voice.wav"
        transcript = self._client.audio.transcriptions.create(
            model=self.transcribe_model,
            file=audio_file,
        )
        text = getattr(transcript, "text", "")
        if not text or not text.strip():
            raise RuntimeError("The transcription provider returned no text.")
        return text.strip()
