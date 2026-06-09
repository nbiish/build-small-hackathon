"""
Calming script generation using the Hugging Face Inference API
or pre-written templates.

The previous version used Dolphin-X1-8B via llama-cpp-python locally. That
required a heavy build step on HF Spaces. This version uses the serverless
HF Inference API and enforces a per-project cooldown via
`shared.inference_client` to protect credit budgets.

Override model: set `CRITTERCALM_MODEL` env var. Default is
`Qwen/Qwen2.5-7B-Instruct` (small, fast, free-tier friendly). The
system prompt is unchanged — output format is identical.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Repo-root path setup so we can import shared.inference_client
_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.inference_client import (  # noqa: E402
    chat_messages,
    cooldown_active,
    cooldown_status,
    generate as _client_generate,
    INFERENCE_MODEL as DEFAULT_MODEL,
)

from content.templates import get_template  # noqa: E402

log = logging.getLogger("crittercalm.content")

CALMING_SYSTEM_PROMPT = """You are a compassionate animal behavior expert who creates calming,
soothing spoken messages for pets. Your words will be spoken aloud to the animal.

Guidelines:
- Use simple, rhythmic language with gentle repetition
- Speak directly to the animal using its name if provided
- Match the tone to the situation (soothing for anxiety, steady for storms, etc.)
- Incorporate species-specific calming techniques:
  * Dogs: calm reassurance, short phrases, mention of familiar routines
  * Cats: soft, slow cadence, blink references, safe-space imagery
  * Chickens: gentle clucking sounds described, flock-safety messaging
  * Birds: soft whistles, perch-and-rest imagery
  * Rabbits: gentle burrow imagery, safety themes
  * Horses: steady breathing cues, herd-companion reassurance
- Keep messages between 30 seconds and 3 minutes when spoken
- Never use scary words or raise alarm
- End each message with a gentle fade-out phrase

Output ONLY the spoken script — no stage directions, no explanations."""


def _model() -> str:
    return os.environ.get("CRITTERCALM_MODEL", DEFAULT_MODEL)


def create_script_prompt(
    animal: str,
    situation: str,
    duration_minutes: int,
    pet_name: str = "",
    custom_message: str = "",
) -> str:
    """Build the user prompt for script generation."""
    pet_part = f" The pet's name is \"{pet_name}\"." if pet_name else ""
    custom_part = f" Incorporate this personal note: \"{custom_message}\"" if custom_message else ""
    return (
        f"Write a {duration_minutes}-minute calming spoken message for a {animal} "
        f"that is experiencing {situation}.{pet_part}{custom_part}"
    )


def generate_calming_script(
    animal: str,
    situation: str,
    duration_minutes: int,
    custom_message: str = "",
    pet_name: str = "",
    dolphin_llm=None,  # legacy param — ignored; we use the HF Inference API
) -> str:
    """Generate a calming script using HF Inference API or fallback templates.

    Args:
        animal: Animal type
        situation: Stress situation
        duration_minutes: Target session length
        custom_message: Optional custom message
        pet_name: Optional pet name
        dolphin_llm: Legacy parameter (ignored)

    Returns:
        Generated calming script as a string
    """
    user_prompt = create_script_prompt(
        animal=animal,
        situation=situation,
        duration_minutes=duration_minutes,
        pet_name=pet_name,
        custom_message=custom_message,
    )

    # Try inference (cooldown-aware)
    if not cooldown_active("crittercalm"):
        try:
            messages = chat_messages(CALMING_SYSTEM_PROMPT, user_prompt)
            result = _client_generate(
                project="crittercalm",
                messages=messages,
                max_new_tokens=int(duration_minutes * 200),  # rough token budget
                temperature=0.7,
            )
            script = result.text.strip()
            if script:
                log.info(f"LLM script generated: {len(script)} chars")
                return script
        except RuntimeError:
            # Cooldown — fall through to template
            log.info("crittercalm inference cooldown; using template")
        except Exception as exc:
            log.warning(f"LLM generation failed, using template: {exc}")
    else:
        log.info("crittercalm inference cooldown active; using template")

    # Fallback: pre-written templates
    return get_template(animal, situation, pet_name, custom_message)


def cooldown_snapshot() -> dict:
    return {
        "model": _model(),
        "cooldown": cooldown_status("crittercalm"),
    }
