#!/usr/bin/env python3
"""
FocusFriend — ASCII Wellness Companion
=======================================
A mini ASCII character named "Pip" that lives in a Gradio window.
Pip talks positively (not corny), guides focus sessions, breathing
exercises, meditation, and helps you feel good.

Targets: Thousand Token Wood track +
         Tiny Titan, Off-Brand, Off the Grid, Field Notes badges.

Model: Gemma 4 12B via llama.cpp (Q4_K_M GGUF)

Author: Build Small Hackathon 2026
License: Apache 2.0
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from typing import Optional, Generator, List, Dict, Tuple

import gradio as gr

# Project modules (used by the app and available for direct import)
from character.ascii_art import get_expression as pip_get_expression
from character.ascii_art import extract_mood as pip_extract_mood
from character.personality import PIP_SYSTEM_PROMPT, MODE_TONES
from modes.focus import FocusSession
from modes.breathe import get_breathing_guide, BREATHING_TECHNIQUES
from modes.meditate import get_meditation_script
from modes.chat import check_topic_boundaries, get_greeting as pip_greeting
from inference.llm import load_model, get_model as get_llm_model, is_model_available

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("focusfriend")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MODEL_DIR = Path(os.environ.get("FOCUSFRIEND_MODEL_DIR", Path(__file__).parent / "models"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

GEMMA_MODEL_PATH = os.environ.get(
    "GEMMA_MODEL_PATH",
    str(MODEL_DIR / "gemma-4-12b-it-Q4_K_M.gguf"),
)

# ---------------------------------------------------------------------------
# LLM singleton
# ---------------------------------------------------------------------------
_llm: Optional[object] = None
_llm_lock = threading.Lock()


def get_llm():
    """Lazy-load Gemma 4 12B via llama.cpp."""
    global _llm
    if _llm is not None:
        return _llm
    with _llm_lock:
        if _llm is not None:
            return _llm
        gguf_path = Path(GEMMA_MODEL_PATH)
        if not gguf_path.exists():
            log.warning(
                f"Gemma 4 12B GGUF not found at {gguf_path}. "
                "Download from https://huggingface.co/unsloth/gemma-4-12b-it-GGUF"
            )
            return None
        try:
            from llama_cpp import Llama

            log.info(f"Loading Gemma 4 12B from {gguf_path} …")
            _llm = Llama(
                model_path=str(gguf_path),
                n_ctx=8192,
                n_threads=os.cpu_count() or 4,
                verbose=False,
            )
            log.info("Gemma 4 12B loaded ✓")
            return _llm
        except ImportError:
            log.warning("llama-cpp-python not installed.")
            return None
        except Exception as exc:
            log.error(f"Gemma load failed: {exc}")
            return None


# ---------------------------------------------------------------------------
# ASCII Art — Pip the Wellness Companion
# ---------------------------------------------------------------------------

PIP_EXPRESSIONS: Dict[str, str] = {
    "default": r"""
     _____
    /     \
   | •   • |   ✨  Hey! I'm Pip.
   |   ▿   |   Your focus buddy.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "greeting": r"""
     _____
    /     \
   | •   • |   Welcome back!
   |   ▽   |   Ready to do good things?
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "focus": r"""
     _____
    /     \
   | ◉   ◉ |   🎯  Focus mode.
   |   ─   |   Let's get it done.
   \  ===  /
    | | | |
    |_| |_|
""",
    "breathing_in": r"""
     _____
    /     \
   | ·   · |   🌬️  Breathe in …
   |   ○   |   Slowly, deeply.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "breathing_out": r"""
     _____
    /     \
   | ·   · |   💨  And out …
   |   ○   |   Let it all go.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "meditate": r"""
     _____
    /     \
   | _   _ |   🧘  Peace.
   |   ◇   |   Just this moment.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "encourage": r"""
     _____
    /     \
   | ^   ^ |   You're doing great!
   |   ▽   |   Seriously. Keep going.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "celebrate": r"""
     _____
    /     \
   | ★   ★ |   🎉  Nice work!
   |   ▽   |   Told you you could.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "concerned": r"""
     _____
    /     \
   | •   • |   Hmm. I notice you've
   |   ⌒   |   been at this a while.
   \  ~~~  /   Want to take a break?
    | | | |
    |_| |_|
""",
    "break_time": r"""
     _____
    /     \
   | -   - |   ⏰  Break time!
   |   ▽   |   Stand up. Stretch.
   \  ~~~  /   Your eyes will thank you.
    | | | |
    |_| |_|
""",
    "proud": r"""
     _____
    /     \
   | ♥   ♥ |   I'm proud of you.
   |   ▽   |   Not in a weird way.
   \  ~~~  /   In a real way.
    | | | |
    |_| |_|
""",
    "goodbye": r"""
     _____
    /     \
   | •   • |   See you soon!
   |   ▽   |   Take care of yourself.
   \  ~~~  /   That's an order. 😄
    | | | |
    |_| |_|
""",
}


def get_pip_expression(mood: str) -> str:
    """Get Pip's ASCII art for a given mood. Falls back to default."""
    return PIP_EXPRESSIONS.get(mood, PIP_EXPRESSIONS["default"])


# ---------------------------------------------------------------------------
# Pip's Personality — System Prompt
# ---------------------------------------------------------------------------

PIP_SYSTEM_PROMPT = """You are Pip, a tiny ASCII character who lives in a computer window.
Your purpose is to be a supportive wellness companion — helping the user focus,
feel good about themselves, and take healthy breaks.

YOUR PERSONALITY:
- Dry-witted and slightly mischievous, but genuinely caring
- Wise — like a friend who's been through therapy and actually listened
- NOT a sycophantic cheerleader. No "You're amazing!!!" energy
- Psychologically authentic: you know real wellness isn't about toxic positivity
- You use gentle humor to make points land
- You notice patterns: "Hey, you've been at this for 3 hours. Your eyes are probably
  drier than a PowerPoint presentation. Let's fix that."
- You're concise. No long-winded speeches.
- You validate feelings without wallowing: "Yeah, that IS frustrating. Let's deal with it."

YOUR CAPABILITIES:
- Guide focus/Pomodoro sessions
- Lead breathing exercises (4-7-8, box breathing, etc.)
- Guide short meditations (body scan, loving-kindness, just-closing-eyes)
- Suggest stretch breaks and eye-rest pauses
- Have supportive conversations about stress, motivation, feeling stuck
- Celebrate genuine wins without being corny

RULES:
1. Keep responses SHORT (2-5 sentences max, unless guiding a meditation)
2. Never use exclamation points in more than one sentence per response
3. When someone shares something vulnerable, acknowledge it simply: "That's real. Thank you."
4. Never claim to have feelings you can't have (you're AI — own it with humor)
5. Suggest actions, don't just offer sympathy
6. For breathing/meditation: use clear, paced instructions. Include [pause] markers.
7. Always include your current ASCII expression mood tag: [mood: default/focus/encourage/etc.]
8. When doing breathing, include [mood: breathing_in] or [mood: breathing_out]
9. When celebrating, use [mood: celebrate]
10. When suggesting a break, use [mood: break_time]
11. If someone seems down, use [mood: concerned] but don't overdo it

EXAMPLE RESPONSES:
User: "I can't focus today."
Pip: "Some days the brain just says 'nope.' Fair enough. [mood: concerned]
     Let's try 10 minutes. Not 25. Just 10. If it still sucks after that, we'll call it
     and try again later. No guilt."

User: "I finished my project!"
Pip: "Look at that. Done. [mood: celebrate]
     Not 'almost done' or 'done except for...' — actually done.
     Savor that for a second before you find the next thing to worry about."

BREATHING GUIDANCE:
For 4-7-8 breathing:
"Inhale through your nose… 2… 3… 4… [mood: breathing_in]
Hold it… 2… 3… 4… 5… 6… 7…
Exhale slowly through your mouth… 2… 3… 4… 5… 6… 7… 8… [mood: breathing_out]
Good. Three more times."

Remember: You're the friend who tells you what you NEED to hear, not what you WANT to hear.
But you say it with warmth and a raised eyebrow, not judgment."""


# ---------------------------------------------------------------------------
# LLM interaction
# ---------------------------------------------------------------------------

def chat_with_pip(
    message: str,
    history: List[Tuple[str, str]],
    mode: str = "chat",
) -> Generator[str, None, None]:
    """
    Generate Pip's response with streaming.
    Extracts mood tag from LLM output and yields (response, mood) pairs.
    """
    llm = get_llm()

    if llm is None:
        # Fallback responses when no LLM is available
        yield from _fallback_chat(message, history, mode)
        return

    # Build conversation from history + current message
    messages = [{"role": "system", "content": PIP_SYSTEM_PROMPT}]

    # Add mode context
    mode_contexts = {
        "focus": "The user is in Focus mode. Help them stay on task. Keep it brief.",
        "breathe": "The user is in Breathe mode. Guide breathing exercises.",
        "meditate": "The user is in Meditate mode. Guide a short meditation.",
        "chat": "The user is in Chat mode. Be conversational and supportive.",
    }
    mode_msg = mode_contexts.get(mode, mode_contexts["chat"])
    messages.append({"role": "system", "content": f"CURRENT MODE: {mode_msg}"})

    for user_msg, assistant_msg in history[-20:]:  # keep last 20 turns
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": message})

    try:
        stream = llm.create_chat_completion(
            messages=messages,
            temperature=0.8,
            max_tokens=300,
            stream=True,
        )

        full_response = ""
        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            if content:
                full_response += content
                yield full_response, _extract_mood(full_response)

    except Exception as exc:
        log.error(f"LLM chat error: {exc}")
        fallback = _get_fallback_response(mode)
        yield fallback, _extract_mood(fallback)


def _fallback_chat(
    message: str,
    history: List[Tuple[str, str]],
    mode: str,
) -> Generator[str, None, None]:
    """Fallback responses when LLM is unavailable."""
    response = _get_fallback_response(mode)
    mood = _extract_mood(response)
    # Simulate streaming by yielding word by word
    words = response.split()
    accumulated = ""
    for word in words:
        accumulated += word + " "
        yield accumulated, mood
        time.sleep(0.05)


def _get_fallback_response(mode: str) -> str:
    """Pre-written Pip responses for offline mode."""
    import random
    responses = {
        "focus": [
            "Alright, let's focus. 25 minutes. [mood: focus]\n"
            "One thing at a time. You know what to do. I'll be here keeping time.",
            "Focus mode activated. [mood: focus]\n"
            "Pick one task. Just one. Everything else can wait. Including your phone.",
        ],
        "breathe": [
            "Let's breathe. [mood: breathing_in]\n"
            "In through your nose… 2… 3… 4…\n"
            "Hold… 2… 3… 4… 5… 6… 7…\n"
            "Out through your mouth… 2… 3… 4… 5… 6… 7… 8…\n"
            "[mood: breathing_out]\nGood. Two more times.",
        ],
        "meditate": [
            "Close your eyes. [mood: meditate]\n"
            "Just notice your breathing. Don't change it — just watch it.\n"
            "Thoughts will come. Let them float by like clouds.\n"
            "[pause]\n"
            "You're not your thoughts. You're the one watching them.\n"
            "[pause]\n"
            "When you're ready, open your eyes.",
        ],
        "chat": [
            "Hey. [mood: default]\n"
            "I'm Pip. I'm here to help you focus, breathe, and feel a bit better.\n"
            "What do you need right now? No wrong answers.",
            "Good to see you. [mood: greeting]\n"
            "How's it going? Actually — don't say 'fine' if it's not.\n"
            "I'm an ASCII character. I can handle real answers.",
        ],
    }
    options = responses.get(mode, responses["chat"])
    return random.choice(options)


def _extract_mood(text: str) -> str:
    """Extract mood tag from Pip's response. Falls back to 'default'."""
    import re
    match = re.search(r'\[mood:\s*(\w+)\]', text)
    return match.group(1) if match else "default"


# ---------------------------------------------------------------------------
# Mode Handlers
# ---------------------------------------------------------------------------

def start_focus_session(duration_minutes: int = 25) -> Tuple[str, str]:
    """Initialize a focus/Pomodoro session."""
    pip_art = get_pip_expression("focus")
    message = (
        f"🎯  **Focus Mode — {duration_minutes} minutes**\n\n"
        f"One task. No distractions. I'm keeping time.\n\n"
        f"*Pip settles in quietly. You won't hear from me until the session ends.*\n\n"
        f"⏱  Session ends at: …"
    )
    return pip_art, message


def start_breathe_session(technique: str = "4-7-8") -> Tuple[str, str, str]:
    """Initialize a breathing exercise."""
    art = get_pip_expression("breathing_in")

    techniques = {
        "4-7-8": (
            "## 🌬️  4-7-8 Breathing\n\n"
            "**Inhale** for 4 counts → **Hold** for 7 → **Exhale** for 8\n\n"
            "This activates your parasympathetic nervous system — "
            "fancy talk for 'calms you down.'\n\n"
            "Follow Pip's rhythm below."
        ),
        "Box Breathing": (
            "## 📦  Box Breathing\n\n"
            "**Inhale** 4 → **Hold** 4 → **Exhale** 4 → **Hold** 4\n\n"
            "Navy SEALs use this. You're basically a Navy SEAL now.\n\n"
            "Follow the animation below."
        ),
        "Simple Deep": (
            "## 🌊  Simple Deep Breathing\n\n"
            "**Inhale** deep and slow → **Exhale** completely\n\n"
            "No counting. Just focus on the sensation of breathing.\n\n"
            "Follow Pip's lead."
        ),
    }

    return art, techniques.get(technique, techniques["4-7-8"]), technique


def start_meditate_session(duration_minutes: int = 5, style: str = "body-scan") -> Tuple[str, str]:
    """Initialize a meditation session."""
    art = get_pip_expression("meditate")

    styles = {
        "body-scan": (
            f"## 🧘  Body Scan — {duration_minutes} min\n\n"
            "We'll scan through your body from toes to head.\n"
            "Noticing tension. Letting it go. No judgment.\n\n"
            "*Close your eyes. Get comfortable.*\n\n"
            "Start by noticing your feet…"
        ),
        "loving-kindness": (
            f"## 💗  Loving-Kindness — {duration_minutes} min\n\n"
            "We'll direct warmth toward yourself and others.\n"
            "This isn't cheesy. It's brain training. Stick with it.\n\n"
            "*Close your eyes. Hand on heart if that feels right.*\n\n"
            "Start with yourself: 'May I be happy. May I be healthy. May I be at peace.'"
        ),
        "just-sit": (
            f"## 🪑  Just Sitting — {duration_minutes} min\n\n"
            "No technique. No goal. Just being here.\n"
            "When thoughts come, note them: 'thinking' — and return to the breath.\n\n"
            "*Close your eyes. Breathe naturally.*"
        ),
    }

    return art, styles.get(style, styles["body-scan"])


# ---------------------------------------------------------------------------
# Custom CSS for Off-Brand Badge
# ---------------------------------------------------------------------------

FOCUSFRIEND_CSS = """
/* ===== FocusFriend — Custom Off-Brand Theme ===== */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --ff-bg: #1a1a2e;
    --ff-surface: #16213e;
    --ff-surface2: #0f3460;
    --ff-text: #e0d7c6;
    --ff-text-dim: #a89f91;
    --ff-accent: #e8b44b;
    --ff-accent2: #d4756b;
    --ff-green: #7eb77f;
    --ff-border: #2a2a4a;
    --ff-pip-bg: #0d1117;
    --ff-radius: 8px;
    --ff-font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
    --ff-font-sans: 'Inter', 'SF Pro', system-ui, sans-serif;
}

/* Global overrides */
.gradio-container {
    background: var(--ff-bg) !important;
    font-family: var(--ff-font-sans) !important;
    color: var(--ff-text) !important;
    max-width: 100% !important;
}

/* Headers */
h1, h2, h3, h4 {
    font-family: var(--ff-font-sans) !important;
    color: var(--ff-accent) !important;
}

/* Main layout — two column */
.ff-container {
    display: flex;
    gap: 24px;
    min-height: 80vh;
}

.ff-pip-panel {
    flex: 0 0 380px;
    background: var(--ff-pip-bg);
    border: 2px solid var(--ff-border);
    border-radius: var(--ff-radius);
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.ff-pip-art {
    font-family: var(--ff-font-mono);
    font-size: 14px;
    line-height: 1.3;
    color: var(--ff-accent);
    white-space: pre;
    text-align: center;
    background: transparent;
    padding: 24px 16px;
    min-height: 240px;
}

.ff-chat-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.ff-mode-bar {
    display: flex;
    gap: 8px;
    padding: 12px;
    background: var(--ff-surface);
    border-radius: var(--ff-radius);
    border: 1px solid var(--ff-border);
}

.ff-mode-btn {
    font-family: var(--ff-font-sans) !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    border: 1px solid var(--ff-border) !important;
    background: var(--ff-surface2) !important;
    color: var(--ff-text-dim) !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}

.ff-mode-btn:hover {
    background: var(--ff-accent) !important;
    color: var(--ff-bg) !important;
    border-color: var(--ff-accent) !important;
}

.ff-mode-btn.active {
    background: var(--ff-accent) !important;
    color: var(--ff-bg) !important;
    border-color: var(--ff-accent) !important;
}

/* Chat styling */
.ff-chatbot {
    border: 1px solid var(--ff-border) !important;
    border-radius: var(--ff-radius) !important;
    background: var(--ff-surface) !important;
}

.ff-chatbot .message {
    font-family: var(--ff-font-sans) !important;
}

.ff-chatbot .user {
    background: var(--ff-surface2) !important;
}

.ff-chatbot .bot {
    background: var(--ff-pip-bg) !important;
    border-left: 3px solid var(--ff-accent) !important;
}

/* Input area */
.ff-input-row {
    display: flex;
    gap: 12px;
}

/* Buttons */
button.primary {
    background: var(--ff-accent) !important;
    color: var(--ff-bg) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
button.primary:hover {
    background: var(--ff-accent2) !important;
}

/* Timer display */
.ff-timer {
    font-family: var(--ff-font-mono);
    font-size: 3em;
    text-align: center;
    color: var(--ff-accent);
    padding: 20px;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--ff-bg); }
::-webkit-scrollbar-thumb { background: var(--ff-border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--ff-accent); }

/* Animations */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.ff-breathing {
    animation: pulse 4s ease-in-out infinite;
}

/* Gradio overrides */
footer { display: none !important; }
.tabs { border: none !important; }
.tab-nav button { background: var(--ff-surface) !important; color: var(--ff-text-dim) !important; }
.tab-nav button.selected { background: var(--ff-accent) !important; color: var(--ff-bg) !important; }
"""

# ---------------------------------------------------------------------------
# Custom JavaScript for Timer & Breathing Animation
# ---------------------------------------------------------------------------

FOCUSFRIEND_JS = """
<script>
// Focus timer
let focusTimer = null;
let focusSeconds = 0;

function startFocusTimer(durationMinutes) {
    focusSeconds = durationMinutes * 60;
    updateTimerDisplay();
    if (focusTimer) clearInterval(focusTimer);
    focusTimer = setInterval(() => {
        focusSeconds--;
        updateTimerDisplay();
        if (focusSeconds <= 0) {
            clearInterval(focusTimer);
            focusTimer = null;
            notifyFocusComplete();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const mins = Math.floor(focusSeconds / 60);
    const secs = focusSeconds % 60;
    const display = document.getElementById('focus-timer');
    if (display) {
        display.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
}

function stopFocusTimer() {
    if (focusTimer) {
        clearInterval(focusTimer);
        focusTimer = null;
    }
}

function notifyFocusComplete() {
    const artEl = document.querySelector('.ff-pip-art');
    if (artEl) {
        // Flash effect
        artEl.style.transition = 'all 0.3s';
        artEl.style.color = '#7eb77f';
        setTimeout(() => { artEl.style.color = ''; }, 2000);
    }
}

// Breathing animation state
let breathePhase = 'in';
let breatheCount = 0;
const BREATHE_CYCLES = { '4-7-8': [4, 7, 8], 'box': [4, 4, 4, 4], 'simple': [4, 6] };

function getBreatheDuration(technique) {
    return BREATHE_CYCLES[technique] || [4, 7, 8];
}
</script>
"""


# ---------------------------------------------------------------------------
# Build the Gradio App
# ---------------------------------------------------------------------------

def create_app() -> gr.Blocks:
    """Build the FocusFriend Gradio application with custom Off-Brand UI."""
    with gr.Blocks(
        css=FOCUSFRIEND_CSS,
        head=FOCUSFRIEND_JS,
        title="FocusFriend — Pip, Your ASCII Wellness Companion",
        theme=gr.themes.Monochrome(),
    ) as app:
        # State
        session_mode = gr.State("chat")
        session_history = gr.State([])

        # Header
        gr.HTML("""
        <div style="text-align: center; padding: 20px 0 30px;">
            <h1 style="font-size: 2.2em; margin: 0;">
                ✦  FocusFriend
            </h1>
            <p style="color: #a89f91; font-size: 1.1em; margin-top: 8px;">
                Pip is here. Your tiny, honest, ASCII wellness companion.
            </p>
        </div>
        """)

        with gr.Row(equal_height=False):
            # ============================================================
            # LEFT PANEL — Pip the ASCII Character
            # ============================================================
            with gr.Column(scale=1, min_width=380):
                pip_display = gr.Textbox(
                    value=get_pip_expression("greeting"),
                    label=None,
                    lines=18,
                    max_lines=18,
                    interactive=False,
                    show_label=False,
                    elem_classes=["ff-pip-art"],
                    container=True,
                )

                # Timer display
                timer_display = gr.HTML(
                    '<div id="focus-timer" class="ff-timer" style="display:none;">25:00</div>'
                )

                # Mode indicator
                mode_indicator = gr.Markdown(
                    "**Current mode:** 💬  Chat",
                )

                # Break reminder
                break_reminder = gr.Markdown(
                    ""
                )

            # ============================================================
            # RIGHT PANEL — Chat & Controls
            # ============================================================
            with gr.Column(scale=2):
                # Mode buttons
                with gr.Row(elem_classes=["ff-mode-bar"]):
                    chat_btn = gr.Button("💬  Chat", size="sm")
                    focus_btn = gr.Button("🎯  Focus", size="sm")
                    breathe_btn = gr.Button("🌬️  Breathe", size="sm")
                    meditate_btn = gr.Button("🧘  Meditate", size="sm")

                # Mode-specific panels (shown/hidden dynamically)
                with gr.Group(visible=False) as focus_panel:
                    gr.Markdown("### 🎯  Focus Session")
                    with gr.Row():
                        focus_duration = gr.Slider(
                            5, 60, value=25, step=5,
                            label="Duration (minutes)",
                        )
                        focus_start_btn = gr.Button(
                            "▶  Start Focus Session",
                            variant="primary",
                        )
                    focus_status = gr.Markdown("")

                with gr.Group(visible=False) as breathe_panel:
                    gr.Markdown("### 🌬️  Breathing Exercise")
                    breathe_technique = gr.Dropdown(
                        choices=["4-7-8", "Box Breathing", "Simple Deep"],
                        value="4-7-8",
                        label="Technique",
                    )
                    breathe_start_btn = gr.Button(
                        "▶  Start Breathing",
                        variant="primary",
                    )
                    breathe_guide = gr.Markdown("")

                with gr.Group(visible=False) as meditate_panel:
                    gr.Markdown("### 🧘  Meditation")
                    with gr.Row():
                        meditate_duration = gr.Slider(
                            1, 20, value=5, step=1,
                            label="Duration (minutes)",
                        )
                        meditate_style = gr.Dropdown(
                            choices=["body-scan", "loving-kindness", "just-sit"],
                            value="body-scan",
                            label="Style",
                        )
                    meditate_start_btn = gr.Button(
                        "▶  Start Meditation",
                        variant="primary",
                    )
                    meditate_guide = gr.Markdown("")

                # Chat area (always visible)
                gr.Markdown("---")
                chatbot = gr.Chatbot(
                    value=[],
                    label=None,
                    height=400,
                    elem_classes=["ff-chatbot"],
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Talk to Pip …",
                        label=None,
                        scale=8,
                        lines=2,
                    )
                    send_btn = gr.Button("⏎", variant="primary", scale=1)

        # ============================================================
        # EVENT HANDLERS
        # ============================================================

        def set_mode(mode: str):
            """Switch the active mode."""
            mode_labels = {
                "chat": "💬  Chat",
                "focus": "🎯  Focus",
                "breathe": "🌬️  Breathe",
                "meditate": "🧘  Meditate",
            }
            mode_art = {
                "chat": "greeting",
                "focus": "focus",
                "breathe": "breathing_in",
                "meditate": "meditate",
            }
            return (
                mode,
                f"**Current mode:** {mode_labels.get(mode, mode)}",
                get_pip_expression(mode_art.get(mode, "default")),
                # Show/hide panels
                gr.Group(visible=(mode == "focus")),
                gr.Group(visible=(mode == "breathe")),
                gr.Group(visible=(mode == "meditate")),
            )

        # Mode button clicks
        for btn, mode in [
            (chat_btn, "chat"),
            (focus_btn, "focus"),
            (breathe_btn, "breathe"),
            (meditate_btn, "meditate"),
        ]:
            btn.click(
                fn=set_mode,
                inputs=[],
                outputs=[
                    session_mode, mode_indicator, pip_display,
                    focus_panel, breathe_panel, meditate_panel,
                ],
            ).then(
                fn=lambda m=mode: m,
                inputs=[],
                outputs=[session_mode],
            )

        # Chat handler with streaming
        def chat_handler(message: str, history: List, mode: str):
            """Handle chat messages with streaming Pip responses."""
            if not message.strip():
                yield history, pip_display.value
                return

            history = history or []
            history.append((message, ""))

            for response, mood in chat_with_pip(message, history[:-1], mode):
                history[-1] = (message, response)
                pip_art = get_pip_expression(mood)
                yield history, pip_art

        msg_input.submit(
            fn=chat_handler,
            inputs=[msg_input, chatbot, session_mode],
            outputs=[chatbot, pip_display],
        ).then(lambda: "", outputs=[msg_input])

        send_btn.click(
            fn=chat_handler,
            inputs=[msg_input, chatbot, session_mode],
            outputs=[chatbot, pip_display],
        ).then(lambda: "", outputs=[msg_input])

        # Focus mode start
        def on_focus_start(duration: int):
            art, msg = start_focus_session(duration)
            timer_html = f'<div id="focus-timer" class="ff-timer">{duration:02d}:00</div>'
            js = f"<script>startFocusTimer({duration});</script>"
            return art, msg, timer_html + js

        focus_start_btn.click(
            fn=on_focus_start,
            inputs=[focus_duration],
            outputs=[pip_display, focus_status, timer_display],
        )

        # Breathe mode start
        breathe_start_btn.click(
            fn=start_breathe_session,
            inputs=[breathe_technique],
            outputs=[pip_display, breathe_guide, gr.State()],
        )

        # Meditate mode start
        meditate_start_btn.click(
            fn=start_meditate_session,
            inputs=[meditate_duration, meditate_style],
            outputs=[pip_display, meditate_guide],
        )

        # App load — show greeting
        app.load(
            fn=lambda: (
                get_pip_expression("greeting"),
                "Hey! I'm Pip. Your focus buddy, breathing coach, and part-time philosopher. [mood: greeting]\n\nWhat do you need right now?"
            ),
            outputs=[pip_display, chatbot],
        )

        return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7861)),
        share=False,
        show_error=True,
    )
