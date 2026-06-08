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
from pathlib import Path
from typing import Optional, Dict, List

import gradio as gr
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from gradio import mount_gradio_app

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

MODEL_PATH = os.environ.get(
    "TINYBARD_MODEL_PATH",
    str(Path("/Volumes/1tb-sandisk/ml-models/huggingface/models--mradermacher--VibeThinker-1.5B-GGUF/snapshots/d0d66139a78030a92a582f966b0f7cbbb3b19406/VibeThinker-1.5B.Q8_0.gguf"))
)

# ---------------------------------------------------------------------------
# Llama.cpp Inference Setup
# ---------------------------------------------------------------------------
_llm = None
_llm_failed = False


def get_llm():
    """Lazy-load the GGUF model via llama-cpp-python."""
    global _llm, _llm_failed
    if _llm is not None:
        return _llm
    if _llm_failed:
        return None

    if not Path(MODEL_PATH).exists():
        log.warning(f"Model file not found at {MODEL_PATH}. Fallback mode active.")
        _llm_failed = True
        return None

    try:
        from llama_cpp import Llama
        log.info(f"Loading VibeThinker-1.5B from {MODEL_PATH} ...")
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=int(os.environ.get("TINYBARD_THREADS", "4")),
            verbose=False,
        )
        log.info("Model loaded successfully ✓")
        return _llm
    except Exception as e:
        log.error(f"Failed to load LLM model: {e}")
        _llm_failed = True
        return None


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
# LLM Generation Logic
# ---------------------------------------------------------------------------
def generate_llm_story(prompt: str, max_tokens: int = 150) -> str:
    """Generate story text via llama.cpp."""
    llm = get_llm()
    if not llm:
        return ""
    try:
        response = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            stop=["\n\n", "User:", "Narrator:"],
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        log.error(f"LLM generation error: {e}")
        return ""


def format_prompt(genre: str, history: List[Dict[str, str]], next_instruction: str) -> str:
    """Build the narrative prompt for the LLM."""
    prompt = (
        "You are the narrator of an interactive text adventure game.\n"
        f"Genre: {genre}\n"
        "Rules:\n"
        "1. Write in the second person ('You...').\n"
        "2. Keep descriptions highly atmospheric, but short (under 3 sentences).\n"
        "3. Focus on action, mystery, and choice.\n\n"
    )
    for h in history:
        if h["role"] == "player":
            prompt += f"Player choice: {h['text']}\n"
        else:
            prompt += f"Narrator: {h['text']}\n"

    prompt += f"{next_instruction}\n"
    return prompt


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

            llm = get_llm()
            if not llm:
                result = generate_procedural_step(genre, 0, 100)
                return (
                    result["story"], result["choices"], result["health"],
                    result["step"], result["game_over"],
                    json.dumps(result.get("history", []))
                )

            instruction = "Narrate the beginning of the adventure. What happens first? Do not offer choices yet."
            story = generate_llm_story(format_prompt(genre, [], instruction))
            if not story:
                result = generate_procedural_step(genre, 0, 100)
                return (
                    result["story"], result["choices"], result["health"],
                    result["step"], result["game_over"],
                    json.dumps(result.get("history", []))
                )

            history = [{"role": "narrator", "text": story}]
            choices_instruction = (
                "Provide exactly 3 short, distinct choices for the player. "
                "Format: 1. [choice 1] | 2. [choice 2] | 3. [choice 3]"
            )
            choices_text = generate_llm_story(format_prompt(genre, history, choices_instruction), max_tokens=60)

            choices = _parse_choices(choices_text)
            if len(choices) < 2:
                choices = ["Explore the area", "Check your equipment", "Proceed carefully"]

            return (story, choices[:3], 100, 1, False, json.dumps(history))

        def api_make_choice(choice: str, genre: str, step: int, health: int, history_json: str):
            """Submit a player choice to advance the story. Exposed as MCP tool."""
            try:
                history = json.loads(history_json)
            except Exception:
                history = []

            llm = get_llm()
            step = int(step)
            health = int(health)

            if not llm:
                result = generate_procedural_step(genre, step, health, choice)
                return (
                    result["story"], result["choices"], result["health"],
                    result["step"], result["game_over"],
                    json.dumps(result.get("history", history))
                )

            history.append({"role": "player", "text": choice})

            health_delta = random.choice([-15, 0, 10])
            new_health = max(0, min(100, health + health_delta))

            if new_health <= 0:
                instruction = "The player has run out of health. Narrate a quick, dramatic end. Game Over."
                story = generate_llm_story(format_prompt(genre, history, instruction))
                return (
                    story or "Your strength fails. The adventure ends in darkness.",
                    [], 0, step + 1, True, json.dumps(history)
                )

            if step >= 4:
                instruction = "Narrate the final glorious victory. The adventure ends in success."
                story = generate_llm_story(format_prompt(genre, history, instruction))
                return (
                    story or "You have achieved your goal! You are victorious!",
                    [], new_health, step + 1, True, json.dumps(history)
                )

            instruction = "Narrate what happens next as a result of the player's choice."
            story = generate_llm_story(format_prompt(genre, history, instruction))
            if not story:
                result = generate_procedural_step(genre, step, health, choice)
                return (
                    result["story"], result["choices"], result["health"],
                    result["step"], result["game_over"],
                    json.dumps(result.get("history", history))
                )

            history.append({"role": "narrator", "text": story})

            choices_instruction = (
                "Provide exactly 3 short, distinct choices. "
                "Format: 1. [choice 1] | 2. [choice 2] | 3. [choice 3]"
            )
            choices_text = generate_llm_story(format_prompt(genre, history, choices_instruction), max_tokens=60)

            choices = _parse_choices(choices_text)
            if len(choices) < 2:
                choices = ["Move forward", "Look around", "Rest a moment"]

            return (story, choices[:3], new_health, step + 1, False, json.dumps(history))

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
    """Check if the LLM is loaded."""
    llm = get_llm()
    return {
        "available": llm is not None,
        "model_path": MODEL_PATH,
        "fallback": _llm_failed
    }


# ---------------------------------------------------------------------------
# Game Logic — exposed as both FastAPI (clean JSON) and Gradio (MCP)
# ---------------------------------------------------------------------------
def _run_turn(choice: str, genre: str, step: int, health: int, history: List[Dict]) -> dict:
    """Single source of truth for one adventure turn.

    Returns a dict the frontend can consume directly. Used by both the
    FastAPI /api/game/* endpoints and the Gradio MCP tools.
    """
    llm = get_llm()

    if step == 0:
        # New game
        if not llm:
            return generate_procedural_step(genre, 0, 100)
        instruction = "Narrate the beginning of the adventure. What happens first? Do not offer choices yet."
        story = generate_llm_story(format_prompt(genre, [], instruction))
        if not story:
            return generate_procedural_step(genre, 0, 100)
        history = [{"role": "narrator", "text": story}]
        choices_instruction = (
            "Provide exactly 3 short, distinct choices for the player. "
            "Format: 1. [choice 1] | 2. [choice 2] | 3. [choice 3]"
        )
        choices_text = generate_llm_story(format_prompt(genre, history, choices_instruction), max_tokens=60)
        choices = _parse_choices(choices_text)
        if len(choices) < 2:
            choices = ["Explore the area", "Check your equipment", "Proceed carefully"]
        return {
            "story": story, "choices": choices[:3], "health": 100,
            "step": 1, "game_over": False, "history": history,
        }

    # Subsequent turn
    if not llm:
        return generate_procedural_step(genre, step, health, choice)

    history.append({"role": "player", "text": choice})
    health_delta = random.choice([-15, 0, 10])
    new_health = max(0, min(100, health + health_delta))

    if new_health <= 0:
        instruction = "The player has run out of health. Narrate a quick, dramatic end. Game Over."
        story = generate_llm_story(format_prompt(genre, history, instruction))
        return {
            "story": story or "Your strength fails. The adventure ends in darkness.",
            "choices": [], "health": 0, "step": step + 1, "game_over": True,
            "history": history,
        }

    if step >= 4:
        instruction = "Narrate the final glorious victory. The adventure ends in success."
        story = generate_llm_story(format_prompt(genre, history, instruction))
        return {
            "story": story or "You have achieved your goal! You are victorious!",
            "choices": [], "health": new_health, "step": step + 1, "game_over": True,
            "history": history,
        }

    instruction = "Narrate what happens next as a result of the player's choice."
    story = generate_llm_story(format_prompt(genre, history, instruction))
    if not story:
        return generate_procedural_step(genre, step, health, choice)
    history.append({"role": "narrator", "text": story})

    choices_instruction = (
        "Provide exactly 3 short, distinct choices. "
        "Format: 1. [choice 1] | 2. [choice 2] | 3. [choice 3]"
    )
    choices_text = generate_llm_story(format_prompt(genre, history, choices_instruction), max_tokens=60)
    choices = _parse_choices(choices_text)
    if len(choices) < 2:
        choices = ["Move forward", "Look around", "Rest a moment"]
    return {
        "story": story, "choices": choices[:3], "health": new_health,
        "step": step + 1, "game_over": False, "history": history,
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

# Mount static files
fastapi_app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount Gradio app at /gradio — this creates the API + MCP endpoints
gradio_blocks = create_gradio_app()
mount_gradio_app(fastapi_app, gradio_blocks, path="/gradio")

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "7860"))
    log.info(f"Starting TinyBard on port {port}")
    log.info(f"Frontend: http://localhost:{port}/")
    log.info(f"Gradio API: http://localhost:{port}/gradio/")
    log.info(f"MCP schema: http://localhost:{port}/gradio/gradio_api/mcp/schema")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
