"""
LLM inference wrapper for FocusFriend using llama.cpp + Gemma 4 12B.

Handles lazy loading, streaming, and fallback behavior.
"""

import os
import threading
import logging
from pathlib import Path
from typing import Optional, Generator, List, Dict

log = logging.getLogger("focusfriend.inference")

# Singleton
_llm = None
_llm_lock = threading.Lock()

# Default model path
DEFAULT_MODEL_DIR = Path(os.environ.get("FOCUSFRIEND_MODEL_DIR", Path(__file__).parent.parent / "models"))
DEFAULT_MODEL_PATH = os.environ.get(
    "GEMMA_MODEL_PATH",
    str(DEFAULT_MODEL_DIR / "gemma-4-12b-it-Q4_K_M.gguf"),
)
DEFAULT_N_CTX = int(os.environ.get("GEMMA_N_CTX", "8192"))
DEFAULT_N_THREADS = int(os.environ.get("GEMMA_N_THREADS", str(os.cpu_count() or 4)))


def load_model(
    model_path: str = None,
    n_ctx: int = None,
    n_threads: int = None,
) -> Optional[object]:
    """
    Load the Gemma 4 12B GGUF model via llama.cpp.

    Args:
        model_path: Path to GGUF file. Uses env var / default if not provided.
        n_ctx: Context window size. Default 8192.
        n_threads: CPU threads. Default all cores.

    Returns:
        Llama instance or None if loading fails.
    """
    global _llm

    if _llm is not None:
        return _llm

    with _llm_lock:
        if _llm is not None:
            return _llm

        model_path = model_path or DEFAULT_MODEL_PATH
        n_ctx = n_ctx or DEFAULT_N_CTX
        n_threads = n_threads or DEFAULT_N_THREADS

        gguf_path = Path(model_path)
        if not gguf_path.exists():
            log.warning(
                f"Model not found at {gguf_path}. "
                f"Download: huggingface-cli download unsloth/gemma-4-12b-it-GGUF "
                f"--include 'gemma-4-12b-it-Q4_K_M.gguf' --local-dir {DEFAULT_MODEL_DIR}"
            )
            return None

        try:
            from llama_cpp import Llama

            log.info(f"Loading Gemma 4 12B from {gguf_path}")
            log.info(f"  n_ctx={n_ctx}, n_threads={n_threads}")

            _llm = Llama(
                model_path=str(gguf_path),
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
            log.info("Gemma 4 12B loaded successfully ✓")
            return _llm

        except ImportError:
            log.warning("llama-cpp-python not installed. pip install llama-cpp-python")
            return None
        except Exception as exc:
            log.error(f"Failed to load Gemma 4 12B: {exc}")
            return None


def get_model() -> Optional[object]:
    """Get the current LLM instance (lazy-loads if needed)."""
    global _llm
    if _llm is not None:
        return _llm
    return load_model()


def is_model_available() -> bool:
    """Check if the LLM is loaded and ready."""
    return _llm is not None


def generate_response(
    messages: List[Dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 300,
) -> Optional[str]:
    """
    Generate a non-streaming response from the model.

    Args:
        messages: List of {'role': ..., 'content': ...} dicts
        temperature: Generation temperature
        max_tokens: Max output tokens

    Returns:
        Generated text or None on failure
    """
    model = get_model()
    if model is None:
        return None

    try:
        response = model.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as exc:
        log.error(f"Generation error: {exc}")
        return None


def generate_stream(
    messages: List[Dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 300,
) -> Generator[str, None, None]:
    """
    Generate a streaming response from the model.

    Args:
        messages: List of {'role': ..., 'content': ...} dicts
        temperature: Generation temperature
        max_tokens: Max output tokens

    Yields:
        Text chunks as they arrive
    """
    model = get_model()
    if model is None:
        yield "⚠️  Model not loaded. I'm running on fallback mode right now."
        return

    try:
        stream = model.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content

    except Exception as exc:
        log.error(f"Streaming error: {exc}")
        yield f"\n\n⚠️  Something went wrong: {exc}"


def unload_model():
    """Release the model from memory."""
    global _llm
    _llm = None
