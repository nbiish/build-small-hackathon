"""
Voice cloning utilities for CritterCalm using OmniVoice.
"""

from typing import Optional


__all__ = ["is_omnivoice_available"]


def is_omnivoice_available() -> bool:
    """Check if OmniVoice is installed and importable."""
    try:
        import omnivoice  # noqa: F401
        return True
    except ImportError:
        return False
