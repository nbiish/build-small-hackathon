"""
Audio processing utilities for CritterCalm.
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple


def load_audio(path: str, target_sr: int = 24000) -> Tuple[np.ndarray, int]:
    """Load audio file and resample if needed. Returns (samples, sample_rate)."""
    samples, sr = sf.read(path)
    if sr != target_sr:
        import librosa
        samples = librosa.resample(samples, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    # Convert to mono if stereo
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    return samples, sr


def save_audio(
    samples: np.ndarray,
    path: str,
    sample_rate: int = 24000,
    normalize: bool = True,
) -> str:
    """Save audio samples to file. Normalizes to prevent clipping."""
    if normalize:
        peak = np.abs(samples).max()
        if peak > 0.99:
            samples = samples / peak * 0.95
    sf.write(path, samples, sample_rate)
    return path


def get_audio_duration(path: str) -> float:
    """Return duration of audio file in seconds."""
    samples, sr = sf.read(str(path))
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    return len(samples) / sr


def validate_voice_sample(
    path: str,
    min_duration: float = 3.0,
    max_duration: float = 30.0,
) -> Optional[str]:
    """
    Validate a voice sample for cloning.
    Returns None if valid, or an error message string.
    """
    import os
    if not os.path.exists(path):
        return "Audio file not found."
    try:
        duration = get_audio_duration(path)
        if duration < min_duration:
            return (
                f"Recording is too short ({duration:.1f}s). "
                f"Please record at least {min_duration:.0f} seconds."
            )
        if duration > max_duration:
            return (
                f"Recording is too long ({duration:.1f}s). "
                f"Please keep it under {max_duration:.0f} seconds."
            )
        return None  # valid
    except Exception as exc:
        return f"Could not read audio file: {exc}"


def estimate_tokens_per_second(text: str) -> float:
    """
    Rough estimate of speech duration based on word count.
    Average English speech is ~150 words per minute (2.5 wps).
    Returns estimated seconds.
    """
    words = len(text.split())
    return words / 2.5
