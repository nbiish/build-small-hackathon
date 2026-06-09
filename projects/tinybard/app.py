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
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import threading

import gradio as gr
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from gradio import mount_gradio_app

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
# User-configurable inference (BYO token / model)
# ---------------------------------------------------------------------------
_USER_CONFIG_LOCK = threading.Lock()
_USER_CONFIG: Dict[str, Optional[str]] = {
    "hf_token": None,
    "model": None,
}


def get_user_hf_token() -> Optional[str]:
    with _USER_CONFIG_LOCK:
        return _USER_CONFIG["hf_token"]


def get_user_model() -> Optional[str]:
    with _USER_CONFIG_LOCK:
        return _USER_CONFIG["model"]


# ---------------------------------------------------------------------------
# Llama.cpp Inference Setup
# ---------------------------------------------------------------------------
# No local LLM state — every inference call goes through the HF Inference API
# with cooldown enforcement. Procedural fallback is always available.


def llm_available() -> bool:
    """True if we *might* succeed at an inference call (cooldown not active,
    HF_TOKEN configured, model id is set)."""
    import os
    token = get_user_hf_token() or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    model = get_user_model() or TINYBARD_MODEL
    # Inference API still works anonymously for some models, so don't gate hard.
    return bool(model) and not cooldown_active("tinybard")


def last_inference_status() -> dict:
    """Snapshot of the current cooldown + model for /api/model_status."""
    return {
        "model": get_user_model() or TINYBARD_MODEL,
        "cooldown": cooldown_status("tinybard"),
        "has_user_token": bool(get_user_hf_token()),
    }


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
            "game_over": False
        }

    health_delta = random.choice([-15, 0, 10])
    new_health = max(0, min(100, health + health_delta))

    if new_health <= 0:
        return {
            "story": f"After choosing: '{choice}'. " + genre_data["lose"],
            "choices": [],
            "health": 0,
            "step": step + 1,
            "game_over": True
        }

    if step >= 4:
        return {
            "story": f"After choosing: '{choice}'. " + genre_data["win"],
            "choices": [],
            "health": new_health,
            "step": step + 1,
            "game_over": True
        }

    node = genre_data["nodes"][step % len(genre_data["nodes"])]
    return {
        "story": f"You choose: '{choice}'.\n\n{node['story']}",
        "choices": node["choices"],
        "health": new_health,
        "step": step + 1,
        "game_over": False
    }


# ---------------------------------------------------------------------------
# LLM Generation Logic (HF Inference API + cooldown)
# ---------------------------------------------------------------------------
def _parse_messages(genre: str, history: List[Dict[str, str]], next_instruction: str) -> list[Dict[str, str]]:
    """Translate internal history into OpenAI-style chat messages."""
    system = (
        "You are the narrator of an interactive text adventure game. "
        f"Genre: {genre}. Write in the second person ('You...'). "
        "Keep descriptions highly atmospheric but short (under 3 sentences). "
        "Focus on action, mystery, and choice."
    )
    msgs: List[Dict[str, str]] = [{"role": "system", "content": system}]
    for h in (history or []):
        if h.get("role") == "player":
            msgs.append({"role": "user", "content": h["text"]})
        elif h.get("role") == "narrator":
            msgs.append({"role": "assistant", "content": h["text"]})
    msgs.append({"role": "user", "content": next_instruction})
    return msgs


def generate_llm_turn(
    genre: str,
    history: List[Dict[str, str]],
    current_health: int,
    next_instruction: str,
) -> dict:
    """Generate one full adventure turn via the LLM.

    Returns a dict with keys: story, choices, health_delta, game_over.
    health_delta is typically -15, 0, or +10 (the model decides).
    """
    if cooldown_active("tinybard"):
        log.info("tinybard turn skipped (cooldown active)")
        return {}
    system = (
        "You are the narrator of an interactive text adventure game. "
        f"Genre: {genre}. Write in the second person ('You...'). "
        "Keep descriptions highly atmospheric but short (under 3 sentences). "
        "Focus on action, mystery, and choice. "
        "After the story beat, output exactly 3 short distinct player choices on one line, "
        "in the format: 1. <choice> | 2. <choice> | 3. <choice>"
    )
    user = (
        f"Current health: {current_health}/100. "
        f"History so far: {json.dumps(history[-4:])}. "
        f"{next_instruction} "
        "Also state a health delta of -15, 0, or +10 that reflects how risky this turn was."
    )
    try:
        result = inference_generate(
            project="tinybard",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_new_tokens=220,
            temperature=0.7,
        )
        text = result.text.strip()
    except Exception as e:
        log.warning(f"HF Inference error (fallback to procedural): {e}")
        return {}

    # Split story and choices
    story = text
    choices = []
    health_delta = 0
    for sep in ["\n1.", "\n1. ", " 1.", " Choices:"]:
        if sep in text:
            parts = text.split(sep, 1)
            story = parts[0].strip()
            rest = parts[1].strip()
            choices = _parse_choices("1. " + rest)
            break

    if not choices:
        choices = _parse_choices(text)

    # Extract a simple health delta from the text when possible
    m = re.search(r"health delta\s*[:=]\s*([+-]?\d+)", text, re.IGNORECASE)
    if m:
        try:
            health_delta = int(m.group(1))
        except Exception:
            health_delta = 0
    else:
        health_delta = random.choice([-15, 0, 10])

    new_health = max(0, min(100, current_health + health_delta))
    game_over = new_health <= 0
    return {
        "story": story,
        "choices": choices[:3] if len(choices) >= 2 else [],
        "health_delta": health_delta,
        "new_health": new_health,
        "game_over": game_over,
    }


# ---------------------------------------------------------------------------
# Gradio Blocks — API endpoints (exposed as MCP tools)
# ---------------------------------------------------------------------------
def create_gradio_app() -> gr.Blocks:
    """Build the Gradio Blocks app with API endpoints for MCP integration."""

    with gr.Blocks(title="TinyBard API") as blocks:
        # Hidden state — not rendered in UI, used by API
        genre_input = gr.Textbox(label="Genre", visible=False)
        step_input = gr.Number(label="Step", value=0, visible=False)
        health_input = gr.Number(label="Health", value=100, visible=False)
        choice_input = gr.Textbox(label="Choice", visible=False)
        history_input = gr.Textbox(label="History JSON", value="[]", visible=False)

        # Output fields
        story_output = gr.Textbox(label="Story")
        choices_output = gr.JSON(label="Choices")
        health_output = gr.Number(label="Health")
        step_output = gr.Number(label="Step")
        game_over_output = gr.Checkbox(label="Game Over")
        history_output = gr.Textbox(label="History JSON")

        def api_start_game(genre: str):
            """Start a new interactive text adventure. Exposed as MCP tool."""
            genre = genre.lower()
            if genre not in ["fantasy", "scifi", "cyberpunk"]:
                genre = "fantasy"

            # Try LLM first (will skip if cooldown is active)
            instruction = "Narrate the beginning of the adventure. What happens first? Do not offer choices yet."
            turn = generate_llm_turn(genre, [], 100, instruction)
            if not turn:
                result = generate_procedural_step(genre, 0, 100)
                return (
                    result["story"], result["choices"], result["health"],
                    result["step"], result["game_over"],
                    json.dumps(result.get("history", []))
                )

            history = [{"role": "narrator", "text": turn["story"]}]
            choices = turn["choices"] if len(turn.get("choices", [])) >= 2 else ["Explore the area", "Check your equipment", "Proceed carefully"]
            return (turn["story"], choices[:3], 100, 1, False, json.dumps(history))

        def api_make_choice(choice: str, genre: str, step: int, health: int, history_json: str):
            """Submit a player choice to advance the story. Exposed as MCP tool."""
            try:
                history = json.loads(history_json)
            except Exception:
                history = []

            step = int(step)
            health = int(health)

            history.append({"role": "player", "text": choice})

            instruction = "Narrate what happens next as a result of the player's choice."
            turn = generate_llm_turn(genre, history, health, instruction)
            if not turn:
                result = generate_procedural_step(genre, step, health, choice)
                return (
                    result["story"], result["choices"], result["health"],
                    result["step"], result["game_over"],
                    json.dumps(result.get("history", history))
                )

            history.append({"role": "narrator", "text": turn["story"]})
            choices = turn["choices"] if len(turn.get("choices", [])) >= 2 else ["Move forward", "Look around", "Rest a moment"]

            return (turn["story"], choices[:3], turn["new_health"], step + 1, turn["game_over"], json.dumps(history))

        # Register API endpoints
        gr.Button("Start Game").click(
            fn=api_start_game,
            inputs=[genre_input],
            outputs=[story_output, choices_output, health_output, step_output, game_over_output, history_output],
            api_name="start_game"
        )

        gr.Button("Make Choice").click(
            fn=api_make_choice,
            inputs=[choice_input, genre_input, step_input, health_input, history_input],
            outputs=[story_output, choices_output, health_output, step_output, game_over_output, history_output],
            api_name="make_choice"
        )

    return blocks


def _parse_choices(choices_text: str) -> List[str]:
    """Parse LLM choice output into a list of choices."""
    choices = []
    if "|" in choices_text:
        choices = [c.split(".")[-1].strip() for c in choices_text.split("|")]
    else:
        for line in choices_text.split("\n"):
            if "." in line or any(d in line for d in "123"):
                parts = line.split(".", 1)
                if len(parts) > 1:
                    choices.append(parts[1].strip())
    return choices


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
def _run_turn(choice: str, genre: str, step: int, health: int, history: List[Dict]) -> dict:
    """Single source of truth for one adventure turn.

    Returns a dict the frontend can consume directly. Used by both the
    FastAPI /api/game/* endpoints and the Gradio MCP tools.
    """
    in_cooldown = cooldown_active("tinybard")

    if step == 0:
        if in_cooldown:
            return generate_procedural_step(genre, 0, 100)
        instruction = "Narrate the beginning of the adventure. What happens first? Do not offer choices yet."
        turn = generate_llm_turn(genre, [], 100, instruction)
        if not turn:
            return generate_procedural_step(genre, 0, 100)
        history = [{"role": "narrator", "text": turn["story"]}]
        choices = turn["choices"] if len(turn.get("choices", [])) >= 2 else ["Explore the area", "Check your equipment", "Proceed carefully"]
        return {
            "story": turn["story"], "choices": choices[:3], "health": 100,
            "step": 1, "game_over": False, "history": history,
        }

    if in_cooldown:
        return generate_procedural_step(genre, step, health, choice)

    history.append({"role": "player", "text": choice})
    instruction = "Narrate what happens next as a result of the player's choice."
    turn = generate_llm_turn(genre, history, health, instruction)
    if not turn:
        return generate_procedural_step(genre, step, health, choice)
    history.append({"role": "narrator", "text": turn["story"]})
    choices = turn["choices"] if len(turn.get("choices", [])) >= 2 else ["Move forward", "Look around", "Rest a moment"]
    return {
        "story": turn["story"], "choices": choices[:3],
        "health": turn["new_health"], "step": step + 1,
        "game_over": turn["game_over"], "history": history,
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

@fastapi_app.post("/api/config")
async def update_config(body: dict):
    with _USER_CONFIG_LOCK:
        if body.get("hf_token"):
            _USER_CONFIG["hf_token"] = body["hf_token"].strip() or None
        if body.get("model") and str(body["model"]).strip():
            _USER_CONFIG["model"] = str(body["model"]).strip()
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
# Exported for HF Spaces Gradio SDK (launches once on import)
# ---------------------------------------------------------------------------
app = fastapi_app

# ---------------------------------------------------------------------------
# HF Spaces entrypoint — keep the ASGI server alive
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
