#!/usr/bin/env python3
"""
ᐴ TinyBard ᔔ — Aanishinaabe Mikinaak-Aki / Fire-Fly Storyteller
==================================================================
Custom FastAPI app with Gradio Blocks mounted for MCP tool integration.
Cedar-and-copper CRT terminal frontend served as static HTML.

Aesthetic: Anishinaabe Solarpunk — sky-to-sunrise palette, syllabic framings,
           biophilic motifs, solarpunk hope.

Targets: Thousand Token Wood + Tiny Titan + Llama Champion tracks.
Badges: Llama Champion, Tiny Titan, Off-Brand (custom frontend),
        Off the Grid, Field Notes.
"""

import os
import json
import random
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, List

import gradio as gr
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from gradio import mount_gradio_app
from pydantic import BaseModel

# Inference client with cooldown (no local GGUF, no llama-cpp-python build!)
# Path layout: monorepo/shared/inference_client.py — go up two parents from this file.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.inference_client import (
    InferenceResult,
    cooldown_status,
    cooldown_remaining,
    cooldown_active,
    generate as inference_generate,
    chat_messages,
    INFERENCE_MODEL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("tinybard")

# ---------------------------------------------------------------------------
# Config & Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Use HF Inference API (VibeThinker 1.5B by default — small, fast, free tier).
# Override via Space env var: INFERENCE_MODEL.
# Cooldown enforced in shared.inference_client.
TINYBARD_MODEL = os.environ.get("TINYBARD_MODEL", INFERENCE_MODEL)

# ---------------------------------------------------------------------------
# Llama.cpp Inference Setup
# ---------------------------------------------------------------------------
# No local LLM state — every inference call goes through the HF Inference API
# with cooldown enforcement. Procedural fallback is always available.


def llm_available() -> bool:
    """True if we *might* succeed at an inference call (cooldown not active,
    HF_TOKEN configured, model id is set)."""
    import os
    if not os.environ.get("HF_TOKEN") and not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
        # Inference API still works anonymously for some models, so don't gate hard.
        pass
    return bool(TINYBARD_MODEL) and not cooldown_active("tinybard")


def last_inference_status() -> dict:
    """Snapshot of the current cooldown + model for /api/model_status."""
    return {
        "model": TINYBARD_MODEL,
        "cooldown": cooldown_status("tinybard"),
    }


def strip_option_prefix(choice: str) -> str:
    """Strip 'Option one: ', 'Option 1: ', etc. prefixes from choice text."""
    import re
    cleaned = re.sub(r"^(option\s+(one|two|three|\d+)[\s:\-]*)\s*", "", choice, flags=re.IGNORECASE)
    return cleaned.strip()


def get_kokoro_model_paths():
    """Download (if not cached) and return paths to Kokoro ONNX model and voices bin."""
    from huggingface_hub import hf_hub_download
    repo_id = "fastrtc/kokoro-onnx"
    try:
        onnx_path = hf_hub_download(repo_id=repo_id, filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id=repo_id, filename="voices-v1.0.bin")
        return onnx_path, voices_path
    except Exception as e:
        log.error(f"Failed to download/load Kokoro model from Hugging Face: {e}")
        return None, None


_kokoro_client = None


def get_kokoro_client():
    global _kokoro_client
    if _kokoro_client is not None:
        return _kokoro_client

    try:
        import pathlib
        import ctypes
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper

        # 1. Patch set_data_path
        if not hasattr(EspeakWrapper, "set_data_path"):
            @classmethod
            def set_data_path(cls, path):
                cls._data_path = pathlib.Path(path) if path else None
            EspeakWrapper.set_data_path = set_data_path

        # 2. Patch ctypes.cdll.LoadLibrary globally to fix espeak_Initialize NULL crash on macOS
        if not hasattr(ctypes.cdll, "_orig_load_library"):
            orig_load = ctypes.cdll.LoadLibrary
            ctypes.cdll._orig_load_library = orig_load

            def patched_load_library(path, *args, **kwargs):
                lib = orig_load(path, *args, **kwargs)
                if "libespeak-ng" in str(path) or "espeak" in str(path):
                    orig_initialize = lib.espeak_Initialize
                    def patched_initialize(output, buflength, path_arg, options):
                        if not path_arg:
                            d_path = espeakng_loader.get_data_path()
                            path_arg = d_path.encode('utf-8')
                        return orig_initialize(output, buflength, path_arg, options)
                    lib.espeak_Initialize = patched_initialize
                return lib
            ctypes.cdll.LoadLibrary = patched_load_library

    except Exception as patch_err:
        log.warning(f"Failed to patch phonemizer/ctypes: {patch_err}")

    onnx_path, voices_path = get_kokoro_model_paths()
    if not onnx_path or not voices_path:
        log.warning("Kokoro model files are not available.")
        return None

    try:
        from kokoro_onnx import Kokoro
        _kokoro_client = Kokoro(onnx_path, voices_path)
        log.info("Kokoro TTS successfully initialized for TinyBard ✓")
        return _kokoro_client
    except Exception as e:
        log.error(f"Failed to initialize Kokoro client: {e}")
        return None

def cleanup_old_audio(audio_dir: Path, max_age_seconds: int = 300):
    """Delete audio files older than max_age_seconds to save disk space."""
    import time
    try:
        now = time.time()
        for f in audio_dir.glob("*.wav"):
            if f.is_file() and (now - f.stat().st_mtime) > max_age_seconds:
                try:
                    f.unlink()
                except Exception:
                    pass
    except Exception as e:
        log.warning(f"Error during audio cleanup: {e}")


MOOD_MAPPING = {
    "cutesy": {"voice": "af_nicole", "speed": 1.1},
    "fun": {"voice": "af_heart", "speed": 1.05},
    "adventurous": {"voice": "af_sarah", "speed": 1.0},
    "mystery": {"voice": "af_bella", "speed": 0.85},
    "sci-fi": {"voice": "am_michael", "speed": 0.95},
    "cyberpunk": {"voice": "am_michael", "speed": 1.05},
}


def clean_tts_text(text: str) -> str:
    cleaned = text.replace("*", "").replace("_", "").replace("`", "")
    import re
    cleaned = re.sub(r"\[MOOD:\s*[^\]]+\]", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def generate_tts_for_turn(story_text: str, choices: List[str], genre: str) -> tuple[Optional[str], Optional[str]]:
    """
    Generate TTS audio for the given story and choices.
    Returns (relative_url, local_filepath) or (None, None) if failed.
    """
    import uuid
    import numpy as np
    import soundfile as sf
    import re

    audio_dir = STATIC_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    cleanup_old_audio(audio_dir)

    kokoro = get_kokoro_client()
    if not kokoro:
        log.warning("Kokoro client not initialized, skipping TTS generation.")
        return None, None

    mood_match = re.search(r"\[MOOD:\s*([a-zA-Z0-9_\-]+)\]", story_text)
    if mood_match:
        mood = mood_match.group(1).lower()
    else:
        if genre == "cyberpunk":
            mood = "cyberpunk"
        elif genre == "scifi":
            mood = "sci-fi"
        elif genre == "fantasy":
            mood = "adventurous"
        else:
            mood = "fun"

    clean_story = re.sub(r"\[MOOD:\s*[a-zA-Z0-9_\-]+\]", "", story_text).strip()
    clean_story = clean_tts_text(clean_story)

    script_parts = [clean_story]

    prefixed_choices_text = []
    prefixes = ["Option one", "Option two", "Option three"]
    for i, choice in enumerate(choices[:3]):
        clean_choice = strip_option_prefix(choice)
        prefixed_choices_text.append(f"{prefixes[i]}: {clean_choice}")

    if prefixed_choices_text:
        script_parts.append(" ".join(prefixed_choices_text))

    full_script = "\n\n".join(script_parts)
    log.info(f"Generating TTS for mood '{mood}':\n{full_script}")

    mood_config = MOOD_MAPPING.get(mood, {"voice": "af_sarah", "speed": 1.0})
    voice = mood_config["voice"]
    speed = mood_config["speed"]

    try:
        sentences = []
        for p in full_script.split("\n\n"):
            for s in p.split("."):
                s_strip = s.strip()
                if s_strip:
                    sentences.append(s_strip + ".")

        chunks = []
        sample_rate = 24000
        for i, sentence in enumerate(sentences):
            samples, sr = kokoro.create(
                text=sentence,
                voice=voice,
                speed=speed,
                lang="en-us"
            )
            chunks.append(samples)
            sample_rate = sr

        if not chunks:
            return None, None

        audio_data = np.concatenate(chunks)

        filename = f"turn_{uuid.uuid4().hex}.wav"
        output_path = audio_dir / filename
        sf.write(str(output_path), audio_data, sample_rate)

        log.info(f"TTS generated successfully: {output_path}")
        return f"/static/audio/{filename}", str(output_path)
    except Exception as e:
        log.exception(f"Failed to generate TTS audio: {e}")
        return None, None


# ---------------------------------------------------------------------------
# Procedural Fallback Adventure Engine
# ---------------------------------------------------------------------------
GENRES = {
    "fantasy": {
        "start": "You stand before the gates of the Whisperwood. The ancient trees hum with a faint violet energy.",
        "nodes": [
            {
                "story": "A glowing sprite appears, offering a golden key or a mossy vial.",
                "choices": ["Take the golden key", "Drink the mossy vial", "Ignore the sprite and press forward"]
            },
            {
                "story": "You encounter a moss-covered stone golem blocking the path. It speaks in riddles.",
                "choices": ["Answer its riddle with a joke", "Use your golden key if you have it", "Try to climb over it"]
            },
            {
                "story": "You discover a hidden pool reflecting stars that aren't in the sky.",
                "choices": ["Drink from the star pool", "Rest by the shore", "Toss a coin into the water"]
            }
        ],
        "win": "You find the heart of the forest and unlock the ancient relic. You are victorious!",
        "lose": "The energy of the forest overwhelms you. You fade into the whispers of the wood."
    },
    "scifi": {
        "start": "The emergency lights flicker red in the derelict cargo bay of USS Horizon. Gravity is failing.",
        "nodes": [
            {
                "story": "A leaking fuel pipe blocks the corridor ahead. Sparking wires fill the air.",
                "choices": ["Siphon the fuel", "Bypass the circuits", "Wait for the cycle to clear"]
            },
            {
                "story": "An automated security drone activates, targeting you with its laser system.",
                "choices": ["Hack the drone terminal", "Throw scrap metal to distract it", "Run for the airlock"]
            },
            {
                "story": "You reach the main computer terminal. The AI core is corrupt but online.",
                "choices": ["Initiate override protocol", "Ask the AI for help", "Pull the main power breaker"]
            }
        ],
        "win": "You restore life support and secure the escape pod. You survive!",
        "lose": "The hull breaches. You are swept into the cold embrace of outer space."
    },
    "cyberpunk": {
        "start": "Acid rain beats against the neon signs of Sector 9. Your neural interface is glitching.",
        "nodes": [
            {
                "story": "A street dealer offers to patch your wetware for a few credits or a favor.",
                "choices": ["Accept the shady patch", "Decline and buy a neural booster", "Threaten him for info"]
            },
            {
                "story": "A corporate agent corners you in a wet alleyway. He demands your datapad.",
                "choices": ["Upload a virus to his cyber-eyes", "Hand over a fake datapad", "Sprint up the fire escape"]
            },
            {
                "story": "You infiltrate the mainframe room of Shinra-Tech. The security grid is active.",
                "choices": ["Jack in directly", "Use your backup deck", "Short-circuit the access node"]
            }
        ],
        "win": "You upload the corporate secrets to the net. Sector 9 is free. You win!",
        "lose": "Your brain fried due to feedback from the security grid. Game Over."
    }
}


def generate_procedural_step(genre: str, step: int, health: int, choice: str = "") -> dict:
    """Generate a fallback adventure step without LLM."""
    genre_data = GENRES.get(genre.lower(), GENRES["fantasy"])

    if step == 0:
        return {
            "story": genre_data["start"],
            "choices": genre_data["nodes"][0]["choices"],
            "health": health,
            "step": 1,
            "game_over": False,
            "genre": genre,
        }

    health_delta = random.choice([-15, 0, 10])
    new_health = max(0, min(100, health + health_delta))

    if new_health <= 0:
        return {
            "story": f"After choosing: '{choice}'. " + genre_data["lose"],
            "choices": [],
            "health": 0,
            "step": step + 1,
            "game_over": True,
            "genre": genre,
        }

    node = genre_data["nodes"][step % len(genre_data["nodes"])]
    return {
        "story": f"You choose: '{choice}'.\n\n{node['story']}",
        "choices": node["choices"],
        "health": new_health,
        "step": step + 1,
        "game_over": False,
        "genre": genre,
    }


# ---------------------------------------------------------------------------
# LLM Generation Logic (HF Inference API + cooldown)
# ---------------------------------------------------------------------------
def _parse_messages(genre: str, history: List[Dict[str, str]], next_instruction: str) -> list[Dict[str, str]]:
    """Translate internal history into OpenAI-style chat messages.

    Includes the last 3 story beats as context for coherent narrative flow.
    """
    system = (
        "You are Nanaboozhoo, the trickster storyteller of Anishinaabe tradition. "
        "You spin interactive text adventures with wit, mischief, and wonder. "
        f"Genre: {genre}. Write in the second person ('You...'). "
        "Keep descriptions atmospheric but concise (2-3 sentences). "
        "Be unpredictable — every story beat should surprise. "
        "Never repeat the same scene twice. "
        "Focus on action, mystery, and choice. Do not offer numbered choices unless asked. "
        "At the very end of your response, append a single tag indicating the mood of this scene "
        "from one of these: [MOOD: cutesy], [MOOD: adventurous], [MOOD: mystery], [MOOD: sci-fi], [MOOD: cyberpunk], [MOOD: fun]. "
        "Choose the mood that best fits the scene. Example: 'You step into the dark corridor. [MOOD: mystery]'"
    )
    msgs: List[Dict[str, str]] = [{"role": "system", "content": system}]

    # Include last 3 history entries as context (most recent first for relevance)
    recent_history = (history or [])[-6:]  # Last 6 entries = ~3 story beats (player + narrator pairs)
    for h in recent_history:
        if h.get("role") == "player":
            msgs.append({"role": "user", "content": h["text"]})
        elif h.get("role") == "narrator":
            msgs.append({"role": "assistant", "content": h["text"]})

    msgs.append({"role": "user", "content": next_instruction})
    return msgs


def generate_llm_story(
    genre: str,
    history: List[Dict[str, str]],
    next_instruction: str,
    max_tokens: int = 180,
) -> str:
    """Generate story text via HF Inference API (with cooldown)."""
    from shared.inference_client import force_clear_cooldown
    force_clear_cooldown("tinybard")
    try:
        msgs = _parse_messages(genre, history, next_instruction)
        result = inference_generate(
            project="tinybard",
            messages=msgs,
            max_new_tokens=max_tokens,
            temperature=0.7,
        )
        return result.text
    except RuntimeError:
        return ""
    except Exception as e:
        log.warning(f"HF Inference error (fallback to procedural): {e}")
        return ""


def generate_llm_choices(genre: str, story_context: str, history: List[Dict[str, str]] | None = None) -> List[str]:
    """Ask the LLM to produce 3 verb-based action choices for the player."""
    from shared.inference_client import force_clear_cooldown
    force_clear_cooldown("tinybard")

    # Build history context for coherent choices
    history_context = ""
    if history:
        recent = history[-4:]  # Last 2 story beats
        history_context = "\n".join(
            f"{'Player' if h.get('role') == 'player' else 'Narrator'}: {h.get('text', '')[:200]}"
            for h in recent
        )

    system = (
        "You generate 3 short, action-oriented player choices for an interactive text adventure. "
        "Each choice MUST start with a verb (action word). Examples: "
        "'Investigate the glowing tree', 'Run toward the fire', 'Hide behind the rocks', "
        "'Speak to the stranger', 'Examine the artifact', 'Search for clues'. "
        "NEVER use descriptive phrases like 'The forest is dark' or 'Something glitters'. "
        "Output exactly 3 choices, one per line, no numbering, no bullets."
    )
    user = (
        f"Genre: {genre}.\n"
        f"Recent story context:\n{history_context}\n\n"
        f"Current situation: {story_context[:300]}\n\n"
        f"Generate 3 verb-based action choices:"
    )
    try:
        result = inference_generate(
            project="tinybard",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_new_tokens=150,
            temperature=0.6,
        )
        raw = result.text.strip() if result.text else ""
        log.info(f"[choices] raw LLM output: {raw!r}")
        choices = _parse_choices(raw)
        log.info(f"[choices] parsed {len(choices)} choices: {choices}")
        return choices
    except Exception:
        log.exception("[choices] LLM choice generation failed")
        return []


# ---------------------------------------------------------------------------
# Gradio Blocks — API endpoints (exposed as MCP tools)
# ---------------------------------------------------------------------------
def create_gradio_app() -> gr.Blocks:
    """Build the Gradio Blocks app with Anishinaabe Solarpunk CRT aesthetic.

    API endpoints (start_game, make_choice) are preserved for MCP integration.
    On HF Spaces, this Gradio UI IS the only interface.
    """

    # Anishinaabe Solarpunk CRT custom CSS
    ASP_CSS = """
    :root {
        --asp-sky:      #5BA4D9;
        --asp-water:    #1B4965;
        --asp-frost:    #CAF0F8;
        --asp-sun:      #F2A93B;
        --asp-sunlight: #FFB347;
        --asp-ember:    #E76F51;
        --asp-birch:    #F5F1E8;
        --asp-moss:     #588157;
        --asp-spruce:   #1B4332;
        --asp-night:    #0F1A2C;
        --asp-earth:    #8B3A1F;
        --asp-stone:    #A89F91;
    }

    /* Page background */
    .gradio-container, .app, body {
        background:
            radial-gradient(ellipse at top, #1B4965 0%, transparent 60%),
            radial-gradient(ellipse at bottom right, #1B4332 0%, transparent 70%),
            #0F1A2C !important;
        color: #F5F1E8 !important;
        font-family: Georgia, 'Iowan Old Style', serif !important;
    }

    /* CRT scanline overlay */
    .gradio-container::after {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(91, 164, 217, 0.04) 2px,
            rgba(91, 164, 217, 0.04) 4px
        );
        pointer-events: none;
        z-index: 9999;
    }

    /* Banner */
    .asp-banner {
        background: linear-gradient(95deg, #5BA4D9 0%, #1B4965 100%);
        color: #F5F1E8;
        border: 1px solid rgba(255, 179, 71, 0.3);
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 16px;
        font-family: Georgia, serif;
        text-align: center;
        text-shadow: 0 1px 2px rgba(15, 26, 44, 0.45);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        letter-spacing: 0.5px;
    }
    .asp-banner .syll { font-size: 1.6em; opacity: 0.9; }
    .asp-banner .glyph { color: #FFB347; font-size: 1.15em; }
    .asp-banner .title {
        font-size: 1.1em; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase;
    }
    .asp-banner .subtitle {
        color: #CAF0F8; font-size: 0.85em;
        font-style: italic; opacity: 0.85;
    }

    /* Section containers */
    .asp-section {
        background: linear-gradient(160deg, rgba(139, 58, 31, 0.25) 0%, rgba(15, 26, 44, 0.6) 100%);
        border: 1px solid rgba(91, 164, 217, 0.2);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow:
            inset 0 0 40px rgba(0, 0, 0, 0.3),
            0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .asp-section::before {
        content: "\\25C8";
        display: block;
        color: #F2A93B;
        font-size: 0.7rem;
        letter-spacing: 6px;
        margin-bottom: 6px;
        opacity: 0.5;
        text-align: center;
    }

    /* Section labels */
    .asp-label {
        color: #CAF0F8 !important;
        font-family: Georgia, serif !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        margin-bottom: 8px !important;
        text-shadow: 0 0 6px rgba(91, 164, 217, 0.3);
    }

    /* Genre radio buttons */
    .asp-genre label {
        background: rgba(15, 26, 44, 0.4) !important;
        border: 1px solid rgba(91, 164, 217, 0.3) !important;
        border-radius: 4px !important;
        color: #CAF0F8 !important;
        padding: 10px 18px !important;
        font-family: Georgia, serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    .asp-genre label:hover {
        background: rgba(242, 169, 59, 0.15) !important;
        border-color: #F2A93B !important;
        color: #FFB347 !important;
        text-shadow: 0 0 12px rgba(242, 169, 59, 0.5);
    }
    .asp-genre input[type="radio"]:checked + span {
        color: #FFB347 !important;
        text-shadow: 0 0 8px rgba(242, 169, 59, 0.5);
    }

    /* Choice radio buttons */
    .asp-choices label {
        display: block !important;
        background: rgba(15, 26, 44, 0.3) !important;
        border: 1px solid rgba(91, 164, 217, 0.25) !important;
        border-radius: 3px !important;
        color: #CAF0F8 !important;
        padding: 10px 16px !important;
        margin-bottom: 4px !important;
        font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Menlo, monospace !important;
        font-size: 0.82rem !important;
        cursor: pointer !important;
        transition: all 0.15s !important;
        text-shadow: 0 0 3px rgba(91, 164, 217, 0.2);
    }
    .asp-choices label:hover {
        background: rgba(91, 164, 217, 0.1) !important;
        border-color: #F2A93B !important;
        color: #FFB347 !important;
        padding-left: 26px !important;
        box-shadow: 0 0 12px rgba(242, 169, 59, 0.15);
    }

    /* Buttons */
    .asp-btn {
        background: linear-gradient(95deg, rgba(139, 58, 31, 0.4) 0%, rgba(27, 67, 50, 0.4) 100%) !important;
        border: 1px solid rgba(91, 164, 217, 0.35) !important;
        border-radius: 4px !important;
        color: #CAF0F8 !important;
        font-family: Georgia, serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        padding: 10px 22px !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .asp-btn:hover {
        background: linear-gradient(95deg, rgba(242, 169, 59, 0.25) 0%, rgba(91, 164, 217, 0.25) 100%) !important;
        border-color: #F2A93B !important;
        color: #FFB347 !important;
        box-shadow: 0 0 18px rgba(242, 169, 59, 0.3);
        text-shadow: 0 0 8px rgba(242, 169, 59, 0.4);
    }
    .asp-btn-primary {
        background: linear-gradient(95deg, #8B3A1F 0%, #1B4332 100%) !important;
        border-color: rgba(242, 169, 59, 0.5) !important;
        box-shadow: 0 0 16px rgba(242, 169, 59, 0.15);
    }
    .asp-btn-primary:hover {
        box-shadow: 0 0 24px rgba(242, 169, 59, 0.4) !important;
    }

    /* Story output */
    .asp-story textarea {
        background: rgba(15, 26, 44, 0.5) !important;
        border: none !important;
        border-left: 3px solid #F2A93B !important;
        border-radius: 0 6px 6px 0 !important;
        color: #F5F1E8 !important;
        font-family: Georgia, 'Iowan Old Style', serif !important;
        font-size: 0.92rem !important;
        line-height: 1.7 !important;
        padding: 14px 18px !important;
        text-shadow: 0 0 6px rgba(242, 169, 59, 0.12);
        box-shadow: inset 0 0 30px rgba(15, 26, 44, 0.4);
        animation: fadeSlideIn 0.5s ease-out;
    }

    /* Textbox inputs */
    .asp-input textarea, .asp-input input {
        background: rgba(15, 26, 44, 0.5) !important;
        border: 1px solid rgba(91, 164, 217, 0.3) !important;
        border-radius: 4px !important;
        color: #F5F1E8 !important;
        font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Menlo, monospace !important;
        font-size: 0.88rem !important;
        caret-color: #F2A93B !important;
    }
    .asp-input textarea:focus, .asp-input input:focus {
        border-color: #F2A93B !important;
        box-shadow: 0 0 12px rgba(242, 169, 59, 0.2);
        outline: none !important;
    }

    /* Status row */
    .asp-status {
        background: rgba(15, 26, 44, 0.4) !important;
        border: 1px solid rgba(91, 164, 217, 0.15) !important;
        border-radius: 6px !important;
        padding: 10px 16px !important;
    }
    .asp-status label {
        color: #CAF0F8 !important;
        font-family: Georgia, serif !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }

    /* Footer */
    .asp-footer {
        text-align: center;
        padding: 10px 0 4px;
        border-top: 1px solid rgba(91, 164, 217, 0.15);
        margin-top: 8px;
        font-size: 0.65rem;
        color: #A89F91;
        letter-spacing: 1.5px;
        font-family: Georgia, serif;
    }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    label, .wrap > label {
        color: #CAF0F8 !important;
        font-family: Georgia, serif !important;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(91, 164, 217, 0.25);
        border-radius: 3px;
    }

    @media (max-width: 600px) {
        .asp-banner { padding: 10px 14px; font-size: 0.85em; }
        .asp-section { padding: 12px; }
    }
    """

    with gr.Blocks(title="TinyBard") as blocks:

        blocks.theme = gr.themes.Base(
            primary_hue="amber",
            neutral_hue="slate",
        ).set(
            body_background_fill="#0F1A2C",
            body_text_color="#F5F1E8",
            block_background_fill="rgba(15, 26, 44, 0.3)",
            block_border_color="rgba(91, 164, 217, 0.2)",
            block_label_text_color="#CAF0F8",
            input_background_fill="rgba(15, 26, 44, 0.5)",
            input_border_color="rgba(91, 164, 217, 0.3)",
            button_primary_background_fill="linear-gradient(95deg, #8B3A1F, #1B4332)",
            button_primary_border_color="rgba(242, 169, 59, 0.5)",
            button_primary_text_color="#CAF0F8",
            button_secondary_background_fill="rgba(139, 58, 31, 0.3)",
            button_secondary_border_color="rgba(91, 164, 217, 0.35)",
            button_secondary_text_color="#CAF0F8",
        )

        # Inject CSS via HTML since Gradio 6.0 has no css= param on Blocks
        gr.HTML(f"<style>{ASP_CSS}</style>")

        # Banner
        gr.HTML(
            '<div class="asp-banner">'
            '<span class="syll">\u1434</span> '
            '<span class="glyph">\u263C</span> '
            '<span class="title">TINYBARD</span> '
            '<span class="glyph">\u2618</span> '
            '<span class="subtitle">\u2014 a fire-fly storyteller in cedar and copper \u2014</span> '
            '<span class="syll">\u1514</span>'
            '</div>'
        )

        # Hidden state fields (for internal tracking + MCP API)
        genre_input = gr.Textbox(label="Genre", value="fantasy", visible=False)
        step_input = gr.Number(label="Step", value=0, visible=False)
        health_input = gr.Number(label="Health", value=100, visible=False)
        history_input = gr.Textbox(label="History JSON", value="[]", visible=False)

        # Genre selector
        with gr.Group(elem_classes=["asp-section"]):
            gr.HTML('<div class="asp-label">\u1434 INAABANDA\u0027IWIN / SELECT GENRE \u1514</div>')
            genre_radio = gr.Radio(
                choices=[
                    ("\u263C Aadizookaan / Fantasy", "fantasy"),
                    ("\u25C8 Ishpiming / Sci-Fi", "scifi"),
                    ("\u25C6 Mashkodewaazibi / Cyberpunk", "cyberpunk"),
                ],
                value="fantasy",
                label=None,
                show_label=False,
                elem_classes=["asp-genre"],
            )

        # Story output
        with gr.Group(elem_classes=["asp-section"]):
            gr.HTML('<div class="asp-label">\u1434 AADIZOOKAAN / STORY \u1514</div>')
            story_output = gr.Textbox(
                label="Story",
                show_label=False,
                lines=8,
                max_lines=20,
                interactive=False,
                elem_classes=["asp-story"],
            )

        # Choices radio (populated after game start)
        with gr.Group(elem_classes=["asp-section"]):
            gr.HTML('<div class="asp-label">\u1434 INAABANDA\u0027IWIN / CHOOSE \u1514</div>')
            choice_radio = gr.Radio(
                choices=[],
                label=None,
                show_label=False,
                interactive=True,
                elem_classes=["asp-choices"],
            )

        # Audio Player (auto-plays TTS if available)
        with gr.Group(elem_classes=["asp-section"]):
            gr.HTML('<div class="asp-label">\u1434 AADIZOOKAAN-MADWEEWEBINIGAN / AUDIO NARRATOR \u1514</div>')
            audio_output = gr.Audio(
                label=None,
                show_label=False,
                autoplay=True,  # Automatically plays on updates
                interactive=False,
                type="filepath",
                elem_classes=["asp-audio"],
            )

        # Choice text input (fallback / custom choice)
        with gr.Group(elem_classes=["asp-section"]):
            gr.HTML('<div class="asp-label">\u1434 NINDANOKIMAA / TYPE YOUR ACTION \u1514</div>')
            choice_text_input = gr.Textbox(
                label="Type your choice",
                show_label=False,
                placeholder="Type your action or select above...",
                lines=1,
                max_lines=3,
                elem_classes=["asp-input"],
            )

        # Action buttons
        with gr.Row():
            start_btn = gr.Button(
                "\u263C START GAME",
                variant="primary",
                elem_classes=["asp-btn", "asp-btn-primary"],
                scale=2,
            )
            choice_btn = gr.Button(
                "\u25C8 MAKE CHOICE",
                variant="secondary",
                elem_classes=["asp-btn"],
                scale=2,
            )
            save_btn = gr.Button(
                "\u25C6 SAVE",
                variant="secondary",
                elem_classes=["asp-btn"],
                scale=1,
            )
            load_btn = gr.Button(
                "\u2618 LOAD",
                variant="secondary",
                elem_classes=["asp-btn"],
                scale=1,
            )

        # Save slot input
        with gr.Group(elem_classes=["asp-section"]):
            gr.HTML('<div class="asp-label">\u1434 OZHIIMAAGAN / SAVE SLOT \u1514</div>')
            save_slot_input = gr.Textbox(
                label="Slot Name",
                show_label=False,
                placeholder="my-adventure",
                lines=1,
                elem_classes=["asp-input"],
            )
            save_status = gr.Textbox(
                label="Save Status",
                show_label=False,
                interactive=False,
                lines=1,
                elem_classes=["asp-input"],
            )

        # Status bar
        with gr.Row(elem_classes=["asp-status"]):
            health_output = gr.Number(label="NOOSISKAAZOWIN / Health", value=100, interactive=False)
            step_output = gr.Number(label="DIBIK / Step", value=0, interactive=False)
            game_over_output = gr.Checkbox(label="GIIZHIG / Game Over", value=False, interactive=False)

        # Choices JSON (hidden for MCP/debug)
        choices_output = gr.JSON(label="Choices JSON", visible=False, elem_classes=["asp-json"])
        history_output = gr.Textbox(label="History JSON", visible=False)

        # Footer
        gr.HTML(
            '<div class="asp-footer">'
            '\u1434 TinyBard \u00b7 FastAPI + Gradio + MCP \u00b7 Anishinaabe Solarpunk \u1514'
            '</div>'
        )

        # ================================================================
        # Event Handlers
        # ================================================================

        # Sync genre radio to hidden genre_input
        def sync_genre(genre_val):
            return genre_val or "fantasy"

        genre_radio.change(
            fn=sync_genre,
            inputs=[genre_radio],
            outputs=[genre_input],
        )

        # Sync choice radio selection to text input
        def sync_choice_to_text(radio_val, current_text):
            if radio_val:
                return radio_val
            return current_text

        choice_radio.change(
            fn=sync_choice_to_text,
            inputs=[choice_radio, choice_text_input],
            outputs=[choice_text_input],
        )

        # Update choice radio from choices JSON
        def update_choices_radio(choices_json):
            if not choices_json:
                return gr.update(choices=[], value=None)
            if isinstance(choices_json, list):
                return gr.update(choices=choices_json, value=None)
            return gr.update(choices=[], value=None)

        def api_start_game(genre: str):
            """Start a new interactive text adventure. Exposed as MCP tool."""
            genre = (genre or "fantasy").lower()
            if genre not in ["fantasy", "scifi", "cyberpunk"]:
                genre = "fantasy"
            res = _run_turn(choice="", genre=genre, step=0, health=100, history=[])
            return (
                res["story"], res["choices"], res["health"],
                res["step"], res["game_over"], json.dumps(res["history"]),
                res.get("audio_path")
            )

        def api_make_choice(choice: str, genre: str, step: int, health: int, history_json: str):
            """Submit a player choice to advance the story. Exposed as MCP tool."""
            genre = (genre or "fantasy").lower()
            try:
                history = json.loads(history_json)
            except Exception:
                history = []
            res = _run_turn(choice=choice, genre=genre, step=step, health=health, history=history)
            return (
                res["story"], res["choices"], res["health"],
                res["step"], res["game_over"], json.dumps(res["history"]),
                res.get("audio_path")
            )

        # Helper: resolve choice from radio or text input
        def resolve_choice(choice_text, choice_radio_val):
            """Use text input if filled, otherwise use radio selection."""
            if choice_text and choice_text.strip():
                return choice_text.strip()
            if choice_radio_val:
                return choice_radio_val
            return ""

        # Make Choice: resolve choice, then call api_make_choice
        def handle_make_choice(choice_text, choice_radio_val, genre, step, health, history_json):
            resolved = resolve_choice(choice_text, choice_radio_val)
            if not resolved:
                return (
                    "Please type or select a choice before making your move.",
                    gr.update(), 100, 0, False, "[]",
                    "", gr.update(), None
                )
            story, choices, h, s, go, hist, audio_path = api_make_choice(resolved, genre, step, health, history_json)
            return story, choices, h, s, go, hist, "", gr.update(choices=choices or [], value=None), audio_path

        # Start Game: call api_start_game, clear choice input, update radio
        def handle_start_game(genre):
            story, choices, h, s, go, hist, audio_path = api_start_game(genre)
            return story, choices, h, s, go, hist, "", gr.update(choices=choices or [], value=None), audio_path

        # UI start game button: also updates choices radio and clears text
        start_btn.click(
            fn=handle_start_game,
            inputs=[genre_input],
            outputs=[story_output, choices_output, health_output, step_output, game_over_output, history_output, choice_text_input, choice_radio, audio_output],
            api_name="start_game",
        )

        # UI make choice button: resolves radio/text, updates choices radio
        choice_btn.click(
            fn=handle_make_choice,
            inputs=[choice_text_input, choice_radio, genre_input, step_input, health_input, history_input],
            outputs=[story_output, choices_output, health_output, step_output, game_over_output, history_output, choice_text_input, choice_radio, audio_output],
            api_name="make_choice",
        )

        # Save game handler
        def handle_save(slot_name, genre, step, health, history_json, game_over):
            import urllib.request
            import urllib.error
            if not slot_name or not slot_name.strip():
                return "Please enter a save slot name."
            try:
                history = json.loads(history_json) if history_json else []
            except Exception:
                history = []
            payload = json.dumps({
                "slot_name": slot_name.strip(),
                "genre": genre or "fantasy",
                "step": int(step or 0),
                "health": int(health or 100),
                "history": history,
                "game_over": bool(game_over),
            }).encode()
            try:
                req = urllib.request.Request(
                    "/api/game/save",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req) as resp:
                    result = json.loads(resp.read())
                    return f"Saved to '{result.get('slot_name', slot_name)}'"
            except Exception as e:
                return f"Save failed: {e}"

        save_btn.click(
            fn=handle_save,
            inputs=[save_slot_input, genre_input, step_input, health_input, history_input, game_over_output],
            outputs=[save_status],
        )

        # Load game handler
        def handle_load(slot_name):
            import urllib.request
            if not slot_name or not slot_name.strip():
                return "Enter a slot name to load.", gr.update(), 100, 0, False, "[]", "", None
            try:
                payload = json.dumps({"slot_name": slot_name.strip()}).encode()
                req = urllib.request.Request(
                    "/api/game/load",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req) as resp:
                    result = json.loads(resp.read())
                    if result.get("status") != "ok":
                        return f"Load failed: {result.get('message', 'Unknown error')}", gr.update(), 100, 0, False, "[]", "", None
                    choices = result.get("choices", [])
                    history = result.get("history", [])
                    story = ""
                    if history:
                        for h in reversed(history):
                            if h.get("role") == "narrator":
                                story = h.get("text", "")
                                break
                    return (
                        story or "Game loaded.",
                        gr.update(choices=choices, value=None),
                        result.get("health", 100),
                        result.get("step", 0),
                        result.get("game_over", False),
                        json.dumps(history),
                        f"Loaded '{result.get('slot_name', slot_name)}'",
                        None,
                    )
            except Exception as e:
                return f"Load failed: {e}", gr.update(), 100, 0, False, "[]", "", None

        load_btn.click(
            fn=handle_load,
            inputs=[save_slot_input],
            outputs=[story_output, choice_radio, health_output, step_output, game_over_output, history_input, save_status, audio_output],
        )

    return blocks


def _parse_choices(choices_text: str) -> List[str]:
    """Parse LLM choice output into a list of choices.

    Handles multiple formats:
      - Pipe-delimited: "1. choice | 2. choice | 3. choice"
      - Newline-delimited: "1. choice\n2. choice\n3. choice"
      - Numbered: "1) choice\n2) choice\n3) choice"
      - Bare lines: "choice\nchoice\nchoice"
    Always returns at least 3 choices (pads with procedural fallbacks).
    """
    import re

    if not choices_text or not choices_text.strip():
        return _fallback_choices()

    text = choices_text.strip()

    # Strategy 1: pipe-delimited "1. ... | 2. ... | 3. ..."
    if "|" in text and text.count("|") >= 2:
        raw = [seg.strip() for seg in text.split("|")]
        choices = []
        for seg in raw:
            # Strip leading "1." or "1)" numbering
            cleaned = re.sub(r"^\d+[\.\)]\s*", "", seg).strip()
            if cleaned:
                choices.append(cleaned)
        if len(choices) >= 3:
            return choices[:3]

    # Strategy 2: newline-delimited (numbered or bare lines)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    choices = []
    for ln in lines:
        # Strip leading "1." or "1)" or "1:" numbering
        cleaned = re.sub(r"^\d+[\.\):\-]+\s*", "", ln).strip()
        # Skip lines that look like headers/meta, not choices
        if cleaned and len(cleaned) > 3 and not cleaned.startswith("#") and not cleaned.startswith("Here"):
            choices.append(cleaned)

    if len(choices) >= 3:
        return choices[:3]

    # Strategy 3: comma-separated fallback (rare but some models do this)
    if len(choices) < 3 and "," in text:
        comma_choices = [c.strip() for c in text.split(",") if c.strip()]
        if len(comma_choices) >= 3:
            return [re.sub(r"^\d+[\.\)]\s*", "", c).strip() for c in comma_choices[:3]]

    # Pad with procedural fallbacks if we got some but not 3
    while len(choices) < 3:
        choices.append(_fallback_choices()[len(choices)])

    return choices[:3]


def _fallback_choices() -> List[str]:
    """Return 3 procedural fallback choices when LLM parsing fails."""
    return [
        "Press forward into the unknown",
        "Examine your surroundings carefully",
        "Call out and listen for a response",
    ]


# ---------------------------------------------------------------------------
# FastAPI App — Custom frontend + Gradio API
# ---------------------------------------------------------------------------
fastapi_app = FastAPI(title="TinyBard", docs_url="/docs")


@fastapi_app.get("/", response_class=HTMLResponse)
async def homepage():
    """Serve the retro CRT terminal frontend."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return HTMLResponse("<h1>TinyBard retro terminal under construction!</h1>")
@fastapi_app.get("/api/model_status")
async def model_status():
    """Check the inference client + cooldown status."""
    return last_inference_status()


# ---------------------------------------------------------------------------
# Game Logic — exposed as both FastAPI (clean JSON) and Gradio (MCP)
# ---------------------------------------------------------------------------
def _llm_health_delta(genre: str, choice: str, history: List[Dict]) -> int:
    """Ask the LLM whether the choice was risky (+/-), then fall back to random."""
    from shared.inference_client import force_clear_cooldown
    force_clear_cooldown("tinybard")
    system = (
        "Rate the risk of a player action in a text adventure. "
        "Reply with ONLY a number: -15 (dangerous), 0 (neutral), or +10 (beneficial). "
        "No explanation, just the number."
    )
    user = f"Genre: {genre}. Action: '{choice}'. Risk rating:"
    try:
        result = inference_generate(
            project="tinybard",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_new_tokens=10,
            temperature=0.3,
        )
        text = result.text.strip()
        for token in ["-15", "-10", "0", "+10", "10", "+5", "-5"]:
            if token in text:
                return int(token)
    except Exception:
        pass
    return random.choice([-15, 0, 10])


def _run_turn(choice: str, genre: str, step: int, health: int, history: List[Dict]) -> dict:
    """Single source of truth for one adventure turn."""
    import re
    prefixes = ["Option one", "Option two", "Option three"]

    if step == 0:
        instruction = "Narrate the beginning of the adventure. What happens first? Do not offer choices yet."
        story = generate_llm_story(genre, [], instruction)
        if not story:
            res = generate_procedural_step(genre, 0, 100)
            formatted_choices = [f"{prefixes[i]}: {strip_option_prefix(ch)}" for i, ch in enumerate(res["choices"][:3])]
            audio_url, audio_path = generate_tts_for_turn(res["story"], formatted_choices, genre)
            return {
                "story": res["story"],
                "choices": formatted_choices,
                "health": 100,
                "step": 1,
                "game_over": False,
                "history": res.get("history", []),
                "genre": genre,
                "audio_url": audio_url,
                "audio_path": audio_path,
            }

        history = [{"role": "narrator", "text": story}]
        choices = generate_llm_choices(genre, story, history)
        if len(choices) < 2:
            choices = ["Explore the area", "Check your equipment", "Proceed carefully"]

        formatted_choices = [f"{prefixes[i]}: {strip_option_prefix(ch)}" for i, ch in enumerate(choices[:3])]
        audio_url, audio_path = generate_tts_for_turn(story, formatted_choices, genre)
        clean_story = re.sub(r"\[MOOD:\s*[a-zA-Z0-9_\-]+\]", "", story).strip()

        return {
            "story": clean_story,
            "choices": formatted_choices,
            "health": 100,
            "step": 1,
            "game_over": False,
            "history": history,
            "genre": genre,
            "audio_url": audio_url,
            "audio_path": audio_path,
        }

    clean_choice = strip_option_prefix(choice)
    history.append({"role": "player", "text": clean_choice})

    # Health delta: ask LLM for consequence, fall back to procedural
    health_delta = _llm_health_delta(genre, clean_choice, history)
    new_health = max(0, min(100, health + health_delta))

    if new_health <= 0:
        instruction = "The player has run out of health. Narrate a quick, dramatic end. Game Over."
        story = generate_llm_story(genre, history, instruction)
        final_story = story or "Your strength fails. The adventure ends in darkness."
        audio_url, audio_path = generate_tts_for_turn(final_story, [], genre)
        clean_story = re.sub(r"\[MOOD:\s*[a-zA-Z0-9_\-]+\]", "", final_story).strip()
        return {
            "story": clean_story,
            "choices": [],
            "health": 0,
            "step": step + 1,
            "game_over": True,
            "history": history,
            "genre": genre,
            "audio_url": audio_url,
            "audio_path": audio_path,
        }

    instruction = (
        f"The player chose: '{clean_choice}'. "
        "Narrate what happens next as a direct consequence of this action. "
        "Be specific to their choice — reference what they did and its immediate result."
    )
    story = generate_llm_story(genre, history, instruction)
    if not story:
        res = generate_procedural_step(genre, step, health, clean_choice)
        formatted_choices = [f"{prefixes[i]}: {strip_option_prefix(ch)}" for i, ch in enumerate(res["choices"][:3])]
        audio_url, audio_path = generate_tts_for_turn(res["story"], formatted_choices, genre)
        return {
            "story": res["story"],
            "choices": formatted_choices,
            "health": res["health"],
            "step": res["step"],
            "game_over": res["game_over"],
            "history": res.get("history", history),
            "genre": genre,
            "audio_url": audio_url,
            "audio_path": audio_path,
        }

    history.append({"role": "narrator", "text": story})

    choices = generate_llm_choices(genre, story, history)
    if len(choices) < 2:
        choices = ["Move forward", "Look around", "Rest a moment"]

    formatted_choices = [f"{prefixes[i]}: {strip_option_prefix(ch)}" for i, ch in enumerate(choices[:3])]
    audio_url, audio_path = generate_tts_for_turn(story, formatted_choices, genre)
    clean_story = re.sub(r"\[MOOD:\s*[a-zA-Z0-9_\-]+\]", "", story).strip()

    return {
        "story": clean_story,
        "choices": formatted_choices,
        "health": new_health,
        "step": step + 1,
        "game_over": False,
        "history": history,
        "genre": genre,
        "audio_url": audio_url,
        "audio_path": audio_path,
    }


@fastapi_app.post("/api/game/start")
async def game_start(payload: dict):
    """Start a new adventure. Returns clean JSON.

    Body: {"genre": "fantasy|scifi|cyberpunk"}
    """
    genre = (payload.get("genre") or "fantasy").lower()
    if genre not in ["fantasy", "scifi", "cyberpunk"]:
        genre = "fantasy"
    return _run_turn(choice="", genre=genre, step=0, health=100, history=[])


@fastapi_app.post("/api/game/choice")
async def game_choice(payload: dict):
    """Submit a player choice. Returns clean JSON.

    Body: {
        "choice": str, "genre": str, "step": int, "health": int,
        "history": [{"role": ..., "text": ...}, ...]
    }
    """
    return _run_turn(
        choice=payload.get("choice", ""),
        genre=payload.get("genre", "fantasy"),
        step=int(payload.get("step", 1)),
        health=int(payload.get("health", 100)),
        history=payload.get("history", []),
    )

# ---------------------------------------------------------------------------
# Save/Load System
# ---------------------------------------------------------------------------
SAVES_DIR = BASE_DIR / "saves"
SAVES_DIR.mkdir(exist_ok=True)


@fastapi_app.post("/api/game/save")
async def game_save(payload: dict):
    """Save current game state to a named slot.

    Body: {slot_name, genre, step, health, history, game_over}
    """
    slot_name = payload.get("slot_name", "autosave")
    # Sanitize slot name for filesystem
    safe_name = "".join(c for c in slot_name if c.isalnum() or c in "-_ ").strip()
    if not safe_name:
        safe_name = "autosave"

    save_data = {
        "slot_name": safe_name,
        "genre": payload.get("genre", "fantasy"),
        "step": int(payload.get("step", 0)),
        "health": int(payload.get("health", 100)),
        "history": payload.get("history", []),
        "game_over": payload.get("game_over", False),
        "timestamp": __import__("time").time(),
    }

    save_path = SAVES_DIR / f"{safe_name}.json"
    save_path.write_text(json.dumps(save_data, indent=2))
    log.info(f"Game saved to slot: {safe_name}")
    return {"status": "ok", "slot_name": safe_name, "timestamp": save_data["timestamp"]}


@fastapi_app.get("/api/game/saves")
async def game_saves():
    """List all saved games."""
    saves = []
    for f in sorted(SAVES_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            saves.append({
                "slot_name": data.get("slot_name", f.stem),
                "genre": data.get("genre", "unknown"),
                "step": data.get("step", 0),
                "health": data.get("health", 0),
                "timestamp": data.get("timestamp", 0),
                "game_over": data.get("game_over", False),
            })
        except Exception:
            continue
    return {"saves": saves}


@fastapi_app.post("/api/game/load")
async def game_load(payload: dict):
    """Load a saved game by slot name.

    Body: {slot_name}
    """
    slot_name = payload.get("slot_name", "")
    safe_name = "".join(c for c in slot_name if c.isalnum() or c in "-_ ").strip()
    save_path = SAVES_DIR / f"{safe_name}.json"

    if not save_path.exists():
        return {"status": "error", "message": f"Save '{safe_name}' not found"}

    try:
        data = json.loads(save_path.read_text())
        return {
            "status": "ok",
            "slot_name": data.get("slot_name", safe_name),
            "genre": data.get("genre", "fantasy"),
            "step": data.get("step", 0),
            "health": data.get("health", 100),
            "history": data.get("history", []),
            "game_over": data.get("game_over", False),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@fastapi_app.delete("/api/game/save/{slot_name}")
async def game_delete_save(slot_name: str):
    """Delete a saved game."""
    safe_name = "".join(c for c in slot_name if c.isalnum() or c in "-_ ").strip()
    save_path = SAVES_DIR / f"{safe_name}.json"

    if save_path.exists():
        save_path.unlink()
        log.info(f"Deleted save: {safe_name}")
        return {"status": "ok", "deleted": safe_name}
    return {"status": "error", "message": f"Save '{safe_name}' not found"}


class UserConfig(BaseModel):
    hf_token: Optional[str] = None
    model: Optional[str] = None


@fastapi_app.post("/api/config")
async def update_config(cfg: UserConfig):
    with _USER_CONFIG_LOCK:
        if cfg.hf_token:
            _USER_CONFIG["hf_token"] = cfg.hf_token.strip() or None
        if cfg.model and cfg.model.strip():
            _USER_CONFIG["model"] = cfg.model.strip()
        current = dict(_USER_CONFIG)
    return {
        "status": "ok",
        "model": current["model"] or TINYBARD_MODEL,
        "has_token": bool(current["hf_token"]),
    }


@fastapi_app.get("/api/config")
async def get_config():
    with _USER_CONFIG_LOCK:
        current = dict(_USER_CONFIG)
    return {
        "model": current["model"] or TINYBARD_MODEL,
        "has_token": bool(current["hf_token"]),
    }


# Mount static files
fastapi_app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount Gradio app at /gradio — this creates the API + MCP endpoints
gradio_blocks = create_gradio_app()
mount_gradio_app(fastapi_app, gradio_blocks, path="/gradio")

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # On HF Spaces, the platform handles the server — just launch Gradio
    if os.environ.get("SPACE_ID"):
        log.info("Running on HF Spaces — launching Gradio directly")
        gradio_blocks.launch(server_name="0.0.0.0", server_port=7860)
    else:
        import uvicorn
        port = int(os.environ.get("PORT", "7860"))
        log.info(f"Starting TinyBard on port {port}")
        log.info(f"Frontend: http://localhost:{port}/")
        log.info(f"Gradio API: http://localhost:{port}/gradio/")
        log.info(f"MCP schema: http://localhost:{port}/gradio/gradio_api/mcp/schema")
        uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
