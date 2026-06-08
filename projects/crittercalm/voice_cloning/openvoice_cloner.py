"""
Voice cloning wrapper for CritterCalm using OmniVoice.

Handles:
- Model loading and caching
- Voice cloning from reference audio
- Speech generation with cloned voice
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import soundfile as sf

log = logging.getLogger("crittercalm.voice_cloning")

# Global cache
_omnivoice_model = None
_cloned_voice_embedding: Optional[dict] = None


def load_omnivoice(model_id: str = "k2-fsa/OmniVoice") -> Optional[object]:
    """
    Lazy-load the OmniVoice model.

    Args:
        model_id: Hugging Face model ID

    Returns:
        OmniVoice model instance or None
    """
    global _omnivoice_model
    if _omnivoice_model is not None:
        return _omnivoice_model

    try:
        from omnivoice import OmniVoice
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Loading OmniVoice on {device} …")
        _omnivoice_model = OmniVoice.from_pretrained(
            model_id,
            device_map=device,
            dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        log.info("OmniVoice loaded ✓")
        return _omnivoice_model
    except ImportError:
        log.warning("omnivoice not installed. pip install omnivoice")
        return None
    except Exception as exc:
        log.error(f"OmniVoice load failed: {exc}")
        return None


def clone_voice(
    audio_path: str,
    ref_text: str,
    model: Optional[object] = None,
) -> Tuple[str, Optional[str]]:
    """
    Clone a voice from reference audio.

    Args:
        audio_path: Path to reference audio file
        ref_text: Transcript of what was said in the audio
        model: Optional pre-loaded OmniVoice model

    Returns:
        (status_message, preview_audio_path) tuple
    """
    global _cloned_voice_embedding

    if not audio_path:
        return "⚠️  Please record a voice sample first.", None

    if not ref_text or len(ref_text.strip()) < 5:
        return "⚠️  Please enter the transcript (at least 5 characters).", None

    if model is None:
        model = load_omnivoice()

    if model is None:
        return (
            "❌  OmniVoice model is not loaded. Please:\n"
            "1. Install: `pip install omnivoice`\n"
            "2. Ensure internet for first-time model download\n"
            "3. Check Hugging Face availability"
        ), None

    try:
        # Generate a test phrase with the cloned voice
        test_audio = model.generate(
            text="This is your cloned voice. I'll use this to help calm your pets.",
            ref_audio=audio_path,
            ref_text=ref_text.strip(),
        )

        # Save preview
        preview_path = Path(tempfile.gettempdir()) / "crittercalm_voice_preview.wav"
        sf.write(str(preview_path), test_audio[0], 24000)

        # Cache the voice embedding info
        _cloned_voice_embedding = {
            "ref_audio": audio_path,
            "ref_text": ref_text.strip(),
        }

        log.info("Voice cloned successfully ✓")
        return (
            "✅  Voice cloned successfully! Your voice is ready.\n\n"
            "🎧  Listen to the preview below, then go to **Calm Your Pet** "
            "to generate soothing audio.",
            str(preview_path),
        )
    except Exception as exc:
        log.error(f"Voice cloning error: {exc}")
        return f"❌  Cloning failed: {exc}", None


def speak_with_cloned_voice(
    text: str,
    model: Optional[object] = None,
) -> Optional[Tuple[np.ndarray, int]]:
    """
    Generate speech using the cloned voice.

    Args:
        text: Text to speak
        model: Optional pre-loaded OmniVoice model

    Returns:
        (audio_samples, sample_rate) or None
    """
    global _cloned_voice_embedding

    if _cloned_voice_embedding is None:
        log.warning("No cloned voice available")
        return None

    if model is None:
        model = load_omnivoice()

    if model is None:
        return None

    try:
        audio = model.generate(
            text=text,
            ref_audio=_cloned_voice_embedding["ref_audio"],
            ref_text=_cloned_voice_embedding["ref_text"],
        )
        return audio[0], 24000
    except Exception as exc:
        log.error(f"Cloned voice generation failed: {exc}")
        return None


def clear_cloned_voice():
    """Clear the cached voice embedding."""
    global _cloned_voice_embedding
    _cloned_voice_embedding = None


def is_voice_cloned() -> bool:
    """Check if a voice has been cloned."""
    return _cloned_voice_embedding is not None
