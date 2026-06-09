#!/usr/bin/env python3
"""
CritterCalm — AI Voice Cloning Animal Soother
==============================================
Clone your voice, then generate calming audio for your pets.
Targets: Backyard AI track + Off the Grid, Well-Tuned, Field Notes badges.

Model stack (all ≤32B total):
  - OmniVoice (0.6B) — zero-shot voice cloning from 3-10 sec audio
  - Dolphin-X1-8B (8B) — calming script generation via llama.cpp
  - Kokoro TTS (82M) — fallback built-in soothing voices

Author: Build Small Hackathon 2026
License: Apache 2.0
"""

import os
import sys
import time
import tempfile
import logging
from pathlib import Path
from typing import Optional, Generator

import gradio as gr
import numpy as np
import soundfile as sf

# Project modules
from content.templates import get_template
from content.script_generator import generate_calming_script
from voice_cloning.openvoice_cloner import clone_voice
from utils.audio_utils import load_audio, save_audio, validate_voice_sample

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("crittercalm")

# ---------------------------------------------------------------------------
# Paths — models stored locally or via env vars
# ---------------------------------------------------------------------------
MODEL_DIR = Path(os.environ.get("CRITTERCALM_MODEL_DIR", Path(__file__).parent / "models"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Deprecated: Dolphin GGUF path kept as None. Script generation now uses
# the HF Inference API via content.script_generator (no local GGUF build).
DOLPHIN_MODEL_PATH = None
OMNIVOICE_MODEL_ID = os.environ.get("OMNIVOICE_MODEL_ID", "k2-fsa/OmniVoice")
KOKORO_MODEL_PATH = os.environ.get(
    "KOKORO_MODEL_PATH",
    str(MODEL_DIR / "kokoro-v1.0.onnx"),
)
KOKORO_VOICES_PATH = os.environ.get(
    "KOKORO_VOICES_PATH",
    str(MODEL_DIR / "voices-v1.0.bin"),
)

# ---------------------------------------------------------------------------
# Lazy-loaded model singletons
# ---------------------------------------------------------------------------
_omnivoice_model: Optional[object] = None
_dolphin_llm: Optional[object] = None
_kokoro_tts: Optional[object] = None
_cloned_voice_embedding: Optional[object] = None  # cached voice embedding


def get_omnivoice():
    """Lazy-load OmniVoice (0.6B params, Apache 2.0)."""
    global _omnivoice_model
    if _omnivoice_model is not None:
        return _omnivoice_model
    try:
        from omnivoice import OmniVoice
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Loading OmniVoice on {device} …")
        _omnivoice_model = OmniVoice.from_pretrained(
            OMNIVOICE_MODEL_ID,
            device_map=device,
            dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        log.info("OmniVoice loaded ✓")
        return _omnivoice_model
    except ImportError:
        log.warning("omnivoice not installed. Install with: pip install omnivoice")
        return None
    except Exception as exc:
        log.error(f"OmniVoice load failed: {exc}")
        return None


# Dolphin LLM is no longer used locally. Script generation now uses the
# HF Inference API via content.script_generator. The shim below preserves
# the call sites in case any external MCP tool references it.
def get_dolphin_llm():
    """Deprecated. Returns None — use the HF Inference API via script_generator."""
    return None


def get_kokoro():
    """Lazy-load Kokoro TTS (82M params, Apache 2.0) — fallback voices."""
    global _kokoro_tts
    if _kokoro_tts is not None:
        return _kokoro_tts
    onnx_path = Path(KOKORO_MODEL_PATH)
    voices_path = Path(KOKORO_VOICES_PATH)
    if not onnx_path.exists() or not voices_path.exists():
        log.warning("Kokoro model files not found. "
                     "Download from https://github.com/thewh1teagle/kokoro-onnx")
        return None
    try:
        from kokoro_onnx import Kokoro

        log.info("Loading Kokoro TTS …")
        _kokoro_tts = Kokoro(str(onnx_path), str(voices_path))
        log.info("Kokoro TTS loaded ✓")
        return _kokoro_tts
    except ImportError:
        log.warning("kokoro-onnx not installed. Install with: pip install kokoro-onnx")
        return None
    except Exception as exc:
        log.error(f"Kokoro load failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Voice cloning
# ---------------------------------------------------------------------------

def clone_voice(audio_path: str, ref_text: str) -> Optional[str]:
    """
    Clone a voice from the recorded audio sample.
    Returns a status message and caches the voice embedding.
    """
    global _cloned_voice_embedding

    if not audio_path:
        return "⚠️  Please record a voice sample first."

    if not ref_text or len(ref_text.strip()) < 5:
        return "⚠️  Please enter the transcript of what you said (at least 5 characters)."

    model = get_omnivoice()
    if model is None:
        return (
            "❌  OmniVoice model is not loaded. Please:\n"
            "1. Install: `pip install omnivoice`\n"
            "2. Ensure the model can be downloaded from Hugging Face\n"
            "3. Check your internet connection for first-time model download"
        )

    try:
        log.info(f"Cloning voice from {audio_path} …")
        # Generate a short test phrase with the cloned voice
        test_audio = model.generate(
            text="This is your cloned voice. I'll use this to help calm your pets.",
            ref_audio=audio_path,
            ref_text=ref_text.strip(),
        )
        # Save test output for preview
        preview_path = Path(tempfile.gettempdir()) / "crittercalm_voice_preview.wav"
        sf.write(str(preview_path), test_audio[0], 24000)

        _cloned_voice_embedding = {
            "ref_audio": audio_path,
            "ref_text": ref_text.strip(),
        }
        log.info("Voice cloned successfully ✓")
        return (
            "✅  Voice cloned successfully! Your voice is ready.\n\n"
            "🎧  Listen to the preview below, then go to the **Calm Your Pet** tab "
            "to generate soothing audio."
        ), str(preview_path)
    except Exception as exc:
        log.error(f"Voice cloning error: {exc}")
        return f"❌  Cloning failed: {exc}", None


# ---------------------------------------------------------------------------
# Calming script generation (Dolphin-X1-8B)
# ---------------------------------------------------------------------------

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


def generate_calming_script(
    animal: str,
    situation: str,
    duration_minutes: int,
    custom_message: str = "",
    pet_name: str = "",
) -> str:
    """Generate a calming script using Dolphin-X1-8B or fallback templates."""
    llm = get_dolphin_llm()

    # Build the generation prompt
    duration_words = (
        "very brief, about 30 seconds"
        if duration_minutes <= 1
        else f"about {duration_minutes} minutes when read aloud slowly"
    )
    name_clause = f"named {pet_name}" if pet_name.strip() else ""
    custom_clause = (
        f"\nInclude this personal message naturally: \"{custom_message}\""
        if custom_message.strip()
        else ""
    )

    user_prompt = (
        f"Write a calming spoken message for a {animal} {name_clause}.\n"
        f"Situation: {situation}.\n"
        f"Length: {duration_words}.{custom_clause}\n"
        f"Make it warm, soothing, and specifically tailored to a {animal}'s needs."
    )

    if llm is not None:
        try:
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": CALMING_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            script = response["choices"][0]["message"]["content"].strip()
            log.info(f"LLM script generated: {len(script)} chars")
            return script
        except Exception as exc:
            log.warning(f"LLM generation failed, using template: {exc}")

    # Fallback: pre-written templates
    return _get_template_script(animal, situation, pet_name, custom_message)


def _get_template_script(
    animal: str, situation: str, pet_name: str, custom_message: str
) -> str:
    """Pre-written calming templates for when the LLM is unavailable."""
    from content.templates import get_template

    return get_template(animal, situation, pet_name, custom_message)


# ---------------------------------------------------------------------------
# Audio generation
# ---------------------------------------------------------------------------

def generate_calming_audio(
    animal: str,
    situation: str,
    duration_minutes: int,
    voice_source: str,
    custom_message: str,
    pet_name: str,
    progress: gr.Progress = gr.Progress(),
) -> tuple[Optional[str], Optional[str]]:
    """
    Full pipeline: generate script → speak with chosen voice → output audio.
    Returns (audio_path, info_text).
    """
    if duration_minutes < 1:
        duration_minutes = 1
    if duration_minutes > 30:
        duration_minutes = 30

    progress(0.0, desc="Generating calming script …")
    script = generate_calming_script(
        animal=animal,
        situation=situation,
        duration_minutes=duration_minutes,
        custom_message=custom_message,
        pet_name=pet_name,
    )
    progress(0.3, desc="Script ready. Synthesizing speech …")

    # Pick voice source
    try:
        if voice_source == "Cloned Voice" and _cloned_voice_embedding is not None:
            # Use OmniVoice with cloned embedding
            model = get_omnivoice()
            if model is None:
                raise RuntimeError("OmniVoice unavailable")
            audio = model.generate(
                text=script,
                ref_audio=_cloned_voice_embedding["ref_audio"],
                ref_text=_cloned_voice_embedding["ref_text"],
            )
            sample_rate = 24000
            audio_data = audio[0]

        elif voice_source in ("Soothing Female", "Soothing Male", "Whisper"):
            # Use Kokoro TTS with built-in voices
            kokoro = get_kokoro()
            if kokoro is None:
                raise RuntimeError("Kokoro TTS unavailable")

            voice_map = {
                "Soothing Female": "af_heart",  # warm, gentle female
                "Soothing Male": "am_adam",     # calm male
                "Whisper": "af_bella",          # soft, whisper-like
            }
            voice = voice_map.get(voice_source, "af_heart")

            # Kokoro doesn't take very long text at once; chunk it
            sentences = [s.strip() + "." for s in script.split(".") if s.strip()]
            chunks = []
            sample_rate = 24000

            for i, sentence in enumerate(sentences):
                progress(0.3 + 0.6 * (i / max(len(sentences), 1)),
                         desc=f"Synthesizing … ({i+1}/{len(sentences)})")
                samples, sr = kokoro.create(
                    text=sentence,
                    voice=voice,
                    speed=0.9,  # slightly slower = more soothing
                    lang="en-us",
                )
                chunks.append(samples)

            audio_data = np.concatenate(chunks) if chunks else np.array([])
            sample_rate = sr

        else:
            # Cloned Voice selected but no clone available — fallback to Soothing Female
            progress(0.3, desc="No cloned voice available, using Soothing Female fallback …")
            return generate_calming_audio(
                animal, situation, duration_minutes,
                "Soothing Female", custom_message, pet_name, progress,
            )

        progress(0.95, desc="Saving audio …")
        output_path = Path(tempfile.gettempdir()) / f"crittercalm_{animal}_{situation.replace(' ', '_')}.wav"
        sf.write(str(output_path), audio_data, sample_rate)

        progress(1.0, desc="Done!")
        info = (
            f"🎧  **Your calming audio is ready!**\n\n"
            f"🐾  Animal: **{animal}**\n"
            f"🎯  For: **{situation}**\n"
            f"⏱   Duration: ~{duration_minutes} min\n"
            f"🎤  Voice: **{voice_source}**\n\n"
            f"💡  **Tip:** Play this for your pet when you notice signs of stress. "
            f"Consistency helps — try using it daily."
        )
        return str(output_path), info

    except Exception as exc:
        log.error(f"Audio generation failed: {exc}")
        return None, (
            f"❌  Audio generation failed: {exc}\n\n"
            f"**Script was generated** — here it is:\n\n---\n{script}\n---\n\n"
            f"You can read this aloud to your pet while we troubleshoot."
        )


# ---------------------------------------------------------------------------
# Model status checker
# ---------------------------------------------------------------------------

def get_model_status() -> str:
    """Return a markdown summary of which models are available + cooldown."""
    # Get the current cooldown snapshot from the script generator
    try:
        from content.script_generator import cooldown_snapshot
        snap = cooldown_snapshot()
        cooldown_line = (
            f"Inference model: `{snap['model']}` · "
            f"cooldown: {snap['cooldown']['active']} · "
            f"window: {snap['cooldown']['window_seconds']}s"
        )
    except Exception as e:
        cooldown_line = f"cooldown status unavailable: {e}"
    lines = [f"> {cooldown_line}\n", "| Model | Status | Purpose |", "|-------|--------|---------|"]

    omni = get_omnivoice()
    lines.append(
        f"| OmniVoice (0.6B) | {'✅ Loaded' if omni else '⚠️  Not loaded'} | Voice cloning & TTS |"
    )

    dolphin = get_dolphin_llm()
    lines.append(
        f"| Dolphin-X1-8B | {'✅ Loaded' if dolphin else '⚠️  Not loaded'} | Calming script generation |"
    )

    kokoro = get_kokoro()
    lines.append(
        f"| Kokoro TTS (82M) | {'✅ Loaded' if kokoro else '⚠️  Not loaded'} | Built-in soothing voices |"
    )

    cloned = "✅ Ready" if _cloned_voice_embedding else "— Not yet cloned"
    lines.append(f"| Voice Clone | {cloned} | Your personal voice |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gradio App
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
/* =========================================================================
   CritterCalm — Anishinaabe Solarpunk Theme
   ----------------------------------------------------------------------------
   Your pet's voice from the meadow. Sun, water, moss, and the small winds.
   ========================================================================= */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

:root {
    /* Anishinaabe-Solarpunk palette */
    --asp-sky:       #5BA4D9;
    --asp-water:     #1B4965;
    --asp-ice:       #BEE9E8;
    --asp-frost:     #CAF0F8;
    --asp-sun:       #F2A93B;
    --asp-sunlight:  #FFB347;
    --asp-ember:     #E76F51;
    --asp-birch:     #F5F1E8;
    --asp-terra:     #C8553D;
    --asp-earth:     #8B3A1F;
    --asp-moss:      #588157;
    --asp-forest:    #3D6A4A;
    --asp-spruce:    #1B4332;
    --asp-night:     #0F1A2C;
    --asp-ash:       #3A2A2A;
    --asp-stone:     #A89F91;

    /* Legacy aliases for downstream code */
    --primary:       var(--asp-moss);
    --primary-light: var(--asp-sunlight);
    --bg:            var(--asp-night);
    --card:          #142a3a;
    --text:          var(--asp-birch);
    --accent:        var(--asp-sun);
    --border:        rgba(91, 164, 217, 0.3);
    --warm:          var(--asp-sunlight);
}

body, .gradio-container {
    background:
        radial-gradient(ellipse at top, rgba(91, 164, 217, 0.18) 0%, transparent 60%),
        radial-gradient(ellipse at bottom, rgba(27, 73, 50, 0.25) 0%, transparent 70%),
        var(--asp-night) !important;
    color: var(--text) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    max-width: 100% !important;
    background-attachment: fixed;
}
h1, h2, h3, h4 {
    font-family: 'EB Garamond', 'Iowan Old Style', Georgia, serif !important;
    color: var(--accent) !important;
    font-weight: 700 !important;
    text-shadow: 0 0 20px rgba(242, 169, 59, 0.18);
}

.tab-nav button {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-size: 1.1em !important;
    padding: 12px 24px !important;
    transition: all 0.2s !important;
}
.tab-nav button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 16px rgba(242, 169, 59, 0.25);
}
.tab-nav button.selected {
    background: linear-gradient(95deg, var(--asp-sun) 0%, var(--asp-sunlight) 100%) !important;
    color: var(--asp-night) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 18px rgba(242, 169, 59, 0.35);
}

button.primary {
    background: linear-gradient(95deg, var(--asp-sun) 0%, var(--asp-sunlight) 100%) !important;
    border: none !important;
    color: var(--asp-night) !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    border-radius: 8px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.2s !important;
}
button.primary:hover {
    background: linear-gradient(95deg, var(--asp-sunlight) 0%, var(--asp-birch) 100%) !important;
    box-shadow: 0 0 20px rgba(242, 169, 59, 0.5);
    transform: translateY(-1px);
}

.animal-emoji {
    font-size: 2em;
    filter: drop-shadow(0 0 6px rgba(242, 169, 59, 0.4));
}
.model-status {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    color: var(--text) !important;
}

footer { display: none !important; }

/* === ASP Banner ====================================================== */
.asp-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6em;
    padding: 14px 18px;
    margin-bottom: 18px;
    background: linear-gradient(95deg, var(--asp-sky) 0%, var(--asp-water) 100%);
    color: var(--asp-birch);
    border-bottom: 1px solid rgba(255, 179, 71, 0.35);
    border-radius: 10px;
    font-family: 'EB Garamond', Georgia, serif;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 2px rgba(15, 26, 44, 0.45);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
}
.asp-banner .syll { font-size: 1.5em; opacity: 0.9; }
.asp-banner .title { font-size: 1.1em; font-weight: 600; }
.asp-banner .glyph { color: var(--asp-sunlight); }
.asp-banner .subtitle {
    color: var(--asp-frost);
    font-size: 0.9em;
    font-style: italic;
    opacity: 0.92;
}
"""


def create_app() -> gr.Blocks:
    """Build the CritterCalm Gradio application."""
    with gr.Blocks(
        title="CritterCalm — Maanamewin / Voice Comfort for Pets",
    ) as app:
        # Anishinaabe-Solarpunk banner
        gr.HTML("""
        <div class="asp-banner">
            <span class="syll">ᐴ</span>
            <span class="glyph">☼</span>
            <span class="title">CRITTERCALM</span>
            <span class="glyph">❀</span>
            <span class="subtitle">— Maanamewin: voice-comfort for the four-leggeds —</span>
            <span class="syll">ᔔ</span>
        </div>
        <h3 style="text-align:center; font-style:italic; color: var(--text); margin-top:0; margin-bottom:20px; opacity: 0.85;">
            Clone your voice. Calm your companion. Even across distance.
        </h3>
        <p style="text-align:center; max-width:680px; margin: 0 auto 24px; color: var(--text); line-height:1.6;">
            Animals respond to their person&apos;s voice — it&apos;s their ultimate comfort signal.
            <strong>CritterCalm</strong> clones your voice locally so your pet can hear you even when you&apos;re away.
        </p>
        """)

        # Model status accordion
        with gr.Accordion("🔧  Model Status", open=False):
            model_status = gr.Markdown(get_model_status, every=30)

        with gr.Tabs() as tabs:
            # ============================================================
            # TAB 1 — Clone Your Voice
            # ============================================================
            with gr.Tab("🎤  Clone Your Voice", id="clone"):
                gr.Markdown(
                    """
                    ### Record a 10-second voice sample

                    **Tips for best results:**
                    - 🎙️  Speak clearly in a quiet room
                    - 📝  Say exactly what you type in the transcript box
                    - 🕐  Aim for 5–15 seconds of audio
                    - 😌  Use your natural, gentle voice — the one your pet knows
                    """
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        voice_input = gr.Audio(
                            label="Record your voice",
                            sources=["microphone", "upload"],
                            type="filepath",
                        )
                        ref_text = gr.Textbox(
                            label="What did you say? (transcript)",
                            placeholder="e.g., \"Hello my sweet pup, it's me. You're safe and loved.\"",
                            lines=3,
                        )
                        clone_btn = gr.Button(
                            "🔮  Clone My Voice",
                            variant="primary",
                            size="lg",
                        )
                    with gr.Column(scale=1):
                        clone_status = gr.Markdown(
                            "👆  Record a voice sample and enter the transcript, "
                            "then click **Clone My Voice**."
                        )
                        clone_preview = gr.Audio(
                            label="Voice preview",
                            type="filepath",
                            interactive=False,
                        )

                clone_btn.click(
                    fn=clone_voice,
                    inputs=[voice_input, ref_text],
                    outputs=[clone_status, clone_preview],
                )

            # ============================================================
            # TAB 2 — Calm Your Pet
            # ============================================================
            with gr.Tab("🎧  Calm Your Pet", id="calm"):
                gr.Markdown(
                    """
                    ### Generate a calming audio session for your pet

                    Choose your pet type, what's stressing them, and we'll create
                    a personalized soothing audio track in your voice.
                    """
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        animal_type = gr.Dropdown(
                            label="🐾  Animal Type",
                            choices=[
                                "Dog", "Cat", "Chicken", "Bird",
                                "Rabbit", "Horse",
                            ],
                            value="Dog",
                        )
                        situation = gr.Dropdown(
                            label="🎯  Situation",
                            choices=[
                                "Separation Anxiety",
                                "Thunderstorm / Fireworks",
                                "Vet Visit",
                                "General Calm",
                                "Bedtime",
                                "Travel / Car Ride",
                                "New Environment",
                                "Loud Noises",
                            ],
                            value="Separation Anxiety",
                        )
                        pet_name = gr.Textbox(
                            label="🐶  Pet's Name (optional)",
                            placeholder="e.g., Buddy, Luna, Clucky …",
                        )
                    with gr.Column(scale=1):
                        voice_source = gr.Dropdown(
                            label="🎤  Voice Source",
                            choices=[
                                "Cloned Voice",
                                "Soothing Female",
                                "Soothing Male",
                                "Whisper",
                            ],
                            value="Cloned Voice",
                        )
                        duration = gr.Slider(
                            label="⏱  Session Length (minutes)",
                            minimum=1,
                            maximum=30,
                            value=5,
                            step=1,
                        )
                        custom_msg = gr.Textbox(
                            label="💬  Custom Message (optional)",
                            placeholder="Add a personal message to include …",
                            lines=2,
                        )

                generate_btn = gr.Button(
                    "✨  Generate Calming Audio",
                    variant="primary",
                    size="lg",
                )

                with gr.Row():
                    audio_output = gr.Audio(
                        label="🎧  Your Calming Audio",
                        type="filepath",
                        interactive=False,
                    )
                    output_info = gr.Markdown(
                        "👆  Configure your settings above and click **Generate**."
                    )

                generate_btn.click(
                    fn=generate_calming_audio,
                    inputs=[
                        animal_type, situation, duration,
                        voice_source, custom_msg, pet_name,
                    ],
                    outputs=[audio_output, output_info],
                )

            # ============================================================
            # TAB 3 — About & Science
            # ============================================================
            with gr.Tab("📚  About & Science", id="about"):
                gr.Markdown(
                    """
                    ## 🧠  The Science of Voice & Animal Bonding

                    ### Why animals respond to their owner's voice

                    Research in animal cognition has shown that:

                    - **Dogs** process their owner's voice in the same brain regions humans
                      use for voice recognition. Your voice literally lights up their brain
                      like a familiar face lights up yours. (Andics et al., 2014)

                    - **Cats** show measurable stress reduction (lower cortisol) when they
                      hear their owner's voice, especially in unfamiliar environments.
                      (Saito & Shinozuka, 2013)

                    - **Chickens** and other birds recognize individual human voices and
                      show reduced alarm calls when hearing familiar, calm speech patterns.

                    - **Horses** can distinguish between familiar and unfamiliar human voices
                      and show lower heart rates with familiar voices during stress.

                    ### How CritterCalm helps

                    1. **Voice Cloning** — We use OmniVoice (0.6B params, 646 languages),
                       a state-of-the-art open-source voice cloning model that captures your
                       vocal timbre, rhythm, and emotional tone from just 3–10 seconds of audio.

                    2. **Calming Scripts** — Dolphin-X1-8B generates species-appropriate
                       soothing messages using evidence-based techniques:
                       - Simple, rhythmic language
                       - Familiar routines and references
                       - Gradual calming progression

                    3. **Voice Synthesis** — Your cloned voice speaks the calming script,
                       creating the experience of you being there, even when you're away.

                    ### Best practices

                    - 🕐  **Consistency matters** — use the same audio at the same times daily
                    - 🔊  **Keep volume moderate** — your pet's hearing is more sensitive than yours
                    - 📱  **Pair with positive experiences** — play during treats or petting at first
                    - 🏠  **Start when you're home** — let them associate the sound with your presence
                    - ⏰  **Session length** — start short (2–3 min) and gradually extend

                    ### Privacy & Local-First

                    CritterCalm runs **100% locally** on your device. Your voice recording,
                    cloned voice, and generated audio never leave your computer. No cloud APIs,
                    no data collection, no tracking. 🔌  **Off the Grid**.

                    ### Models used
                    - **OmniVoice** (0.6B) — Xiaomi AI Lab, Apache 2.0
                    - **Dolphin-X1-8B** (8B) — Llama 3.1 derivative, community license
                    - **Kokoro TTS** (82M) — Apache 2.0

                    ---
                    *Built with ❤️  for the Build Small Hackathon 2026*
                    """
                )

        return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        share=False,
        show_error=True,
        mcp_server=True,
        css=CUSTOM_CSS,
    )
