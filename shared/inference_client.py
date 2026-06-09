"""
Shared HF Inference Client + Cooldown
======================================
Lightweight wrapper around `huggingface_hub.InferenceClient` with:

- Per-call cooldown to prevent credit burn on live HF Spaces
- Async-friendly API
- Auto-fallback to procedural/story-template engines when inference fails
- Environment-driven config (works in HF Spaces and local)

The cooldown model:
- Each project has its own cooldown window (default 8s for cheap inference APIs)
- Within a session, after a successful inference, no new call can run until cooldown expires
- Failed inference does not start a cooldown (allow quick retry)
- `cooldown_active()` is the public check; FastAPI handlers short-circuit on active cooldown
"""
from __future__ import annotations

import os
import time
import logging
import threading
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, List

log = logging.getLogger("inference")

# ── Environment knobs ─────────────────────────────────────────────────────────
# Override these in your Space's "Settings → Variables and secrets".

# The HF model id used for text generation (VibeThinker 1.5B, Gemma 4 12B, etc.)
INFERENCE_MODEL = os.environ.get(
    "INFERENCE_MODEL",
    "Qwen/Qwen2.5-1.5B-Instruct",  # small, fast, free-tier friendly
)

# Provider: "hf-inference" (free serverless), "together", "fal-ai", "replicate"
# Free HF inference works for many small models; otherwise use a paid provider.
INFERENCE_PROVIDER = os.environ.get("INFERENCE_PROVIDER", "hf-inference")

# Token — read from HF Space secrets at runtime.
HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")

# Default cooldown between inferences, in seconds.
COOLDOWN_SECONDS = float(os.environ.get("INFERENCE_COOLDOWN_SECONDS", "8"))

# Per-project override (keyed by app name)
PROJECT_COOLDOWN_OVERRIDES = {
    "tinybard": float(os.environ.get("TINYBARD_COOLDOWN_SECONDS", "6")),
    "focusfriend": float(os.environ.get("FOCUSFRIEND_COOLDOWN_SECONDS", "10")),
    "crittercalm": float(os.environ.get("CRITTERCALM_COOLDOWN_SECONDS", "12")),
}

# Max tokens to request (keeps costs bounded)
MAX_NEW_TOKENS = int(os.environ.get("INFERENCE_MAX_TOKENS", "220"))


# ── Cooldown registry ────────────────────────────────────────────────────────
@dataclass
class _CooldownState:
    last_call: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock)


_states: Dict[str, _CooldownState] = {}


def _state(project: str) -> _CooldownState:
    if project not in _states:
        _states[project] = _CooldownState()
    return _states[project]


def cooldown_seconds_for(project: str) -> float:
    return PROJECT_COOLDOWN_OVERRIDES.get(project, COOLDOWN_SECONDS)


def cooldown_active(project: str) -> bool:
    """Return True if the project is currently in cooldown (cannot run inference)."""
    state = _state(project)
    now = time.time()
    if now - state.last_call < cooldown_seconds_for(project):
        return True
    return False


def cooldown_remaining(project: str) -> float:
    """Seconds left in the cooldown window (0 if not in cooldown)."""
    state = _state(project)
    elapsed = time.time() - state.last_call
    remaining = cooldown_seconds_for(project) - elapsed
    return max(0.0, remaining)


def cooldown_status(project: str) -> dict:
    """Snapshot of cooldown state for the UI."""
    return {
        "active": cooldown_active(project),
        "remaining_seconds": round(cooldown_remaining(project), 2),
        "window_seconds": cooldown_seconds_for(project),
    }


def _mark_called(project: str) -> None:
    state = _state(project)
    with state.lock:
        state.last_call = time.time()


# ── Inference client wrapper ─────────────────────────────────────────────────
class InferenceResult:
    """A small wrapper so callers don't need to know which API returned text."""
    def __init__(self, text: str, model: str, provider: str, latency_s: float):
        self.text = text
        self.model = model
        self.provider = provider
        self.latency_s = latency_s

    def __repr__(self) -> str:
        return f"InferenceResult(text={self.text[:50]!r}…, model={self.model!r}, latency={self.latency_s:.2f}s)"


def _get_client():
    """Lazy-load the InferenceClient to keep boot fast."""
    from huggingface_hub import InferenceClient
    return InferenceClient(
        model=INFERENCE_MODEL,
        token=HF_TOKEN,
        provider=INFERENCE_PROVIDER,
    )


def generate(
    project: str,
    messages: List[Dict[str, str]],
    *,
    max_new_tokens: Optional[int] = None,
    temperature: float = 0.7,
) -> InferenceResult:
    """Run a chat-style inference call, with cooldown enforcement.

    `messages` follows OpenAI chat format: [{"role": "user|assistant|system", "content": "..."}].
    Returns InferenceResult with `.text` (string) on success, or raises on failure.
    Caller is responsible for fallback handling.
    """
    if cooldown_active(project):
        remaining = cooldown_remaining(project)
        raise RuntimeError(
            f"cooldown active for {project!r}: {remaining:.1f}s remaining. "
            f"This protects your HF/Modal credit budget."
        )

    max_new_tokens = max_new_tokens or MAX_NEW_TOKENS
    client = _get_client()
    start = time.time()
    response = client.chat_completion(
        messages=messages,
        max_tokens=max_new_tokens,
        temperature=temperature,
    )
    latency = time.time() - start
    text = response.choices[0].message.content or ""
    text = text.strip()
    _mark_called(project)
    return InferenceResult(
        text=text,
        model=INFERENCE_MODEL,
        provider=INFERENCE_PROVIDER,
        latency_s=latency,
    )


def force_clear_cooldown(project: str) -> None:
    """Manual escape hatch (e.g. for testing or admin overrides)."""
    _state(project).last_call = 0.0


# ── Convenience: build messages + format result ──────────────────────────────
def chat_messages(system: str, user: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
    """Build an OpenAI-style message list with optional prior turns.

    `history` is in the same [{role, content}, ...] format. New turns are appended.
    """
    msgs: List[Dict[str, str]] = [{"role": "system", "content": system}]
    if history:
        msgs.extend(history)
    msgs.append({"role": "user", "content": user})
    return msgs


__all__ = [
    "InferenceResult",
    "cooldown_active",
    "cooldown_remaining",
    "cooldown_seconds_for",
    "cooldown_status",
    "force_clear_cooldown",
    "generate",
    "chat_messages",
    "INFERENCE_MODEL",
    "INFERENCE_PROVIDER",
    "MAX_NEW_TOKENS",
]


if __name__ == "__main__":
    # Smoke test
    for p in ("tinybard", "focusfriend", "crittercalm"):
        print(p, "cooldown:", cooldown_status(p))
