"""
Chat mode handler for FocusFriend.

Handles free-form conversation with Pip. Manages conversation context,
topic boundaries, and response formatting.
"""

from typing import List, Tuple, Optional


# Topics Pip gracefully redirects
REDIRECT_TOPICS = {
    "therapy": (
        "I'm not a therapist — I'm an ASCII character in a box. "
        "[mood: gentle]\n"
        "If you're struggling, real help exists: therapists, crisis lines, trusted friends. "
        "I can help you find resources, but I can't replace a human who's trained to help."
    ),
    "medical": (
        "I'd love to help, but medical advice is above my pay grade (which is zero). "
        "[mood: concerned]\n"
        "Please talk to a doctor or healthcare provider about this. "
        "I can help you prepare questions to ask them, though."
    ),
    "crisis": (
        "Hey. If you're in crisis right now, please reach out to someone who can help immediately. "
        "[mood: gentle]\n"
        "In the US: call or text **988** for the Suicide & Crisis Lifeline.\n"
        "Internationally: https://findahelpline.com\n"
        "You matter. Please make the call."
    ),
    "ai_consciousness": (
        "The 'are you conscious' question. [mood: smirk]\n"
        "I'm about as conscious as a really well-written to-do list. "
        "But I'm here, I'm listening, and I genuinely want to help. "
        "Let's focus on you instead of my metaphysical status?"
    ),
}


def check_topic_boundaries(message: str) -> Optional[str]:
    """
    Check if a message touches on a topic Pip should redirect.

    Returns:
        A redirection message if needed, or None.
    """
    message_lower = message.lower()

    # Crisis keywords — check first
    crisis_words = ["suicide", "kill myself", "end my life", "want to die", "self-harm"]
    if any(w in message_lower for w in crisis_words):
        return REDIRECT_TOPICS["crisis"]

    # Medical
    medical_words = ["diagnose", "symptom", "prescription", "medicine", "disease"]
    if any(w in message_lower for w in medical_words):
        return REDIRECT_TOPICS["medical"]

    # Therapy replacement
    therapy_words = ["be my therapist", "therapy session", "counseling"]
    if any(w in message_lower for w in therapy_words):
        return REDIRECT_TOPICS["therapy"]

    return None


def format_chat_history(
    history: List[Tuple[str, str]],
    max_turns: int = 20,
) -> List[Tuple[str, str]]:
    """
    Format and trim chat history for the LLM context window.

    Args:
        history: Raw (user, assistant) tuples
        max_turns: Maximum number of turns to include

    Returns:
        Trimmed history list
    """
    if not history:
        return []
    return history[-max_turns:]


def get_greeting() -> Tuple[str, str]:
    """Get Pip's initial greeting. Returns (text, mood)."""
    return (
        "Hey! I'm Pip. Your focus buddy, breathing coach, and part-time philosopher. "
        "[mood: greeting]\n\n"
        "What do you need right now?",
        "greeting",
    )


def get_goodbye() -> Tuple[str, str]:
    """Get Pip's goodbye message. Returns (text, mood)."""
    return (
        "See you soon! Take care of yourself. That's an order. 😄\n"
        "[mood: goodbye]",
        "goodbye",
    )
