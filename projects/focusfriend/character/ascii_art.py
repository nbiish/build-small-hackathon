"""
ASCII art generation for Pip, the FocusFriend wellness companion.

Pip has multiple expressions mapped to moods. The LLM selects a mood
tag in each response, and we render the corresponding ASCII art.
"""

from typing import Dict, Optional, Tuple
import re


# ============================================================================
# Pip's Expression Library
# ============================================================================

PIP_EXPRESSIONS: Dict[str, str] = {
    # --- Neutral / Default ---
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
    "curious": r"""
     _____
    /     \
   | o   o |   Hmm? Tell me more.
   |   ⌂   |   I'm listening.
   \  ~~~  /
    | | | |
    |_| |_|
""",

    # --- Focus ---
    "focus": r"""
     _____
    /     \
   | ◉   ◉ |   🎯  Focus mode.
   |   ─   |   Let's get it done.
   \  ===  /
    | | | |
    |_| |_|
""",
    "determined": r"""
     _____
    /     \
   | ◉   ◉ |   We're doing this.
   |   ◠   |   No distractions.
   \  ▬▬▬  /
    | | | |
    |_| |_|
""",

    # --- Breathing ---
    "breathing_in": r"""
     _____
    /     \
   | ·   · |   🌬️  Breathe in …
   |   ○   |   Slowly, deeply.
   \  ~~~  /   Fill your lungs.
    | | | |
    |_| |_|
""",
    "breathing_out": r"""
     _____
    /     \
   | ·   · |   💨  And out …
   |   ○   |   Let it all go.
   \  ~~~  /   Release the tension.
    | | | |
    |_| |_|
""",
    "breathing_hold": r"""
     _____
    /     \
   | ·   · |   ✋  Hold …
   |   ◎   |   Just for a moment.
   \  ~~~  /   Suspended. Calm.
    | | | |
    |_| |_|
""",

    # --- Meditation ---
    "meditate": r"""
     _____
    /     \
   | _   _ |   🧘  Peace.
   |   ◇   |   Just this moment.
   \  ~~~  /   Nothing else.
    | | | |
    |_| |_|
""",
    "zen": r"""
     _____
    /     \
   | ‿   ‿ |   …
   |   ○   |   (that's it)
   \  ~~~  /   (just that)
    | | | |
    |_| |_|
""",

    # --- Positive / Encouraging ---
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
    "proud": r"""
     _____
    /     \
   | ♥   ♥ |   I'm proud of you.
   |   ▽   |   Not in a weird way.
   \  ~~~  /   In a real way.
    | | | |
    |_| |_|
""",
    "wink": r"""
     _____
    /     \
   | •   ~ |   You've got this.
   |   ▽   |   *supportive wink*
   \  ~~~  /
    | | | |
    |_| |_|
""",

    # --- Concerned / Care ---
    "concerned": r"""
     _____
    /     \
   | •   • |   Hmm. I noticed you've
   |   ⌒   |   been at this a while.
   \  ~~~  /   Want to take a break?
    | | | |
    |_| |_|
""",
    "gentle": r"""
     _____
    /     \
   | •   • |   Hey. That sounds hard.
   |   ‿   |   I'm here.
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "thoughtful": r"""
     _____
    /     \
   | •   • |   Let me think about
   |   ⌂   |   what you said …
   \  ~~~  /
    | | | |
    |_| |_|
""",

    # --- Break / Rest ---
    "break_time": r"""
     _____
    /     \
   | -   - |   ⏰  Break time!
   |   ▽   |   Stand up. Stretch.
   \  ~~~  /   Your eyes will thank you.
    | | | |
    |_| |_|
""",
    "sleepy": r"""
     _____
    /     \
   | ‿   ‿ |   Getting sleepy …
   |   ○   |   Maybe it's time
   \  ~~~  /   to call it a day?
    | | | |
    |_| |_|
""",

    # --- Humor ---
    "smirk": r"""
     _____
    /     \
   | •   ~ |   Oh really?
   |   ⌣   |   *skeptical eyebrow*
   \  ~~~  /
    | | | |
    |_| |_|
""",
    "laughing": r"""
     _____
    /     \
   | ^   ^ |   Ha! Good one.
   |   ▽   |   You're funnier than
   \  ~~~  /   you think you are.
    | | | |
    |_| |_|
""",

    # --- Goodbye ---
    "goodbye": r"""
     _____
    /     \
   | •   • |   See you soon!
   |   ▽   |   Take care of yourself.
   \  ~~~  /   That's an order. 😄
    | | | |
    |_| |_|
""",
    "wave": r"""
     _____
    /     \
   | •   • |   Bye for now! 👋
   |   ▽   |   Come back when you
   \  ~~~  /   need a friend.
    | | | |
    |_| |_|
""",
}


def get_expression(mood: str) -> str:
    """
    Get Pip's ASCII art for a given mood.

    Args:
        mood: Mood tag like 'focus', 'celebrate', 'concerned', etc.

    Returns:
        Multi-line ASCII art string. Falls back to 'default' if mood not found.
    """
    # Normalize mood string
    mood = mood.lower().strip().replace(" ", "_").replace("-", "_")
    return PIP_EXPRESSIONS.get(mood, PIP_EXPRESSIONS["default"])


def extract_mood(text: str) -> str:
    """
    Extract the [mood: <name>] tag from Pip's response text.

    Args:
        text: The full response text from Pip

    Returns:
        Mood name string, or 'default' if no mood tag found
    """
    match = re.search(r"\[mood:\s*(\w+)\]", text, re.IGNORECASE)
    return match.group(1).lower() if match else "default"


def strip_mood_tag(text: str) -> str:
    """
    Remove the mood tag from display text (for the chat).

    Args:
        text: Response text potentially containing [mood: ...]

    Returns:
        Clean text without the mood tag
    """
    return re.sub(r"\[mood:\s*\w+\]\s*", "", text).strip()


def list_moods() -> list[str]:
    """Return all available mood names."""
    return sorted(PIP_EXPRESSIONS.keys())


def get_mood_category(mood: str) -> str:
    """Return the category a mood belongs to."""
    categories = {
        "neutral": ["default", "greeting", "curious"],
        "focus": ["focus", "determined"],
        "breathing": ["breathing_in", "breathing_out", "breathing_hold"],
        "meditation": ["meditate", "zen"],
        "encouraging": ["encourage", "celebrate", "proud", "wink"],
        "caring": ["concerned", "gentle", "thoughtful"],
        "break": ["break_time", "sleepy"],
        "humor": ["smirk", "laughing"],
        "goodbye": ["goodbye", "wave"],
    }
    mood = mood.lower().strip()
    for category, moods in categories.items():
        if mood in moods:
            return category
    return "neutral"
