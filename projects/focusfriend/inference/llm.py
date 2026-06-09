"""
LLM inference wrapper for FocusFriend using the Hugging Face Inference API.

The previous version loaded a local GGUF (Gemma 4 12B Q4_K_M) via llama-cpp-python.
That required a heavy compile step on HF Spaces and tied us to a single model. This
version uses `huggingface_hub.InferenceClient` (serverless) and enforces a
project-scoped cooldown via `shared.inference_client` to protect your credit budget.

To override the model: set `INFERENCE_MODEL` env var.
Common picks:
- "Qwen/Qwen2.5-7B-Instruct" (default; sweet spot for chat)
- "meta-llama/Meta-Llama-3-8B-Instruct"
- "google/gemma-2-9b-it"
"""
from __future__ import annotations

import logging
import os
import sys
import threading
from pathlib import Path
from typing import Generator, List, Dict, Optional

log = logging.getLogger("focusfriend.inference")

# Add monorepo root so we can import shared.inference_client
_THIS = Path(__file__).resolve()
_PROJECT = _THIS.parent.parent
_REPO_ROOT = _PROJECT.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.inference_client import (  # noqa: E402
    InferenceResult,
    chat_messages,
    cooldown_status,
    cooldown_active,
    generate as _client_generate,
    INFERENCE_MODEL as DEFAULT_MODEL,
)


def _model() -> str:
    """Pick the FocusFriend-specific model, falling back to the default."""
    return os.environ.get("FOCUSFRIEND_MODEL", DEFAULT_MODEL)


def is_model_available() -> bool:
    """True if the inference API is configured (token or anonymous)."""
    if cooldown_active("focusfriend"):
        return False
    has_token = bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
    # Many small models work anonymously; don't gate hard.
    return bool(_model())


def get_model() -> Optional[str]:
    """Return the model id we plan to use. None if no model configured."""
    if not _model():
        return None
    return _model()


def cooldown_snapshot() -> dict:
    """Public status snapshot for the UI."""
    return {
        "model": _model(),
        "cooldown": cooldown_status("focusfriend"),
    }


def generate_response(
    messages: List[Dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 300,
) -> Optional[str]:
    """One-shot generation. Returns text or None on cooldown/failure.

    `messages` follows OpenAI chat format. Caller is responsible for system prompt
    and prior turns.
    """
    if cooldown_active("focusfriend"):
        log.info("focusfriend inference skipped (cooldown active)")
        return None
    try:
        result = _client_generate(
            project="focusfriend",
            messages=messages,
            max_new_tokens=max_tokens,
            temperature=temperature,
        )
        return result.text
    except Exception as exc:
        log.warning(f"HF Inference error: {exc}")
        return None


def generate_stream(
    messages: List[Dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 300,
) -> Generator[str, None, None]:
    """Streaming generator. Yields the full response in chunks.

    The HF Inference API doesn't return true token-level streams from chat_completion
    in the python client, so we yield the full text and let the UI's natural
    chunking handle the appearance of streaming. Falls back to graceful error.
    """
    if cooldown_active("focusfriend"):
        yield "\n\n⏳ Pip is resting. (Inference cooldown — try again in a moment.)"
        return
    try:
        result = _client_generate(
            project="focusfriend",
            messages=messages,
            max_new_tokens=max_tokens,
            temperature=temperature,
        )
        # Simulate streaming by chunking the response on word boundaries
        text = result.text
        if not text:
            yield "\n\n[No response]"
            return
        # Yield in word-sized chunks for natural reading pace
        words = text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else " " + word
            yield chunk
    except Exception as exc:
        yield f"\n\n⚠️  Something went wrong: {exc}"


def unload_model():
    """No-op for serverless inference (kept for API compat)."""
    return


# Re-export for callers that still expect this
load_model = lambda *args, **kwargs: get_model()  # noqa: E731
