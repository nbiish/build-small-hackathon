"""
Meditation mode for FocusFriend.

Pip guides short meditation sessions:
- Body scan
- Loving-kindness (metta)
- Just sitting (shikantaza-style)
"""

from typing import Dict, List, Optional
import random


# Guided meditation scripts
# Each key maps to a pre-written script when LLM is unavailable

MEDITATION_SCRIPTS: Dict[str, Dict] = {
    "body-scan": {
        "name": "Body Scan",
        "description": (
            "Systematically bringing awareness to each part of the body, "
            "noticing sensations, and releasing tension."
        ),
        "script": [
            ("Find a comfortable position. Sitting or lying down — either works.", "meditate"),
            ("Close your eyes gently. Take three deep breaths to settle in.", "breathing_in"),
            ("[pause]", "zen"),
            ("Bring your attention to your feet. Just notice what you feel. Warmth? Coolness? Tingling? Nothing at all? Whatever you notice is fine.", "meditate"),
            ("Now move up to your ankles and lower legs. Any tension there? Let it soften.", "meditate"),
            ("[pause]", "zen"),
            ("Your knees and thighs. Feel the weight of them. Let them be heavy and relaxed.", "meditate"),
            ("[pause]", "zen"),
            ("Your hips and pelvis. This is where many of us hold stress. Breathe into this area and let it release.", "meditate"),
            ("[pause]", "zen"),
            ("Your lower back and belly. Feel the gentle rise and fall of your breath here.", "breathing_in"),
            ("[pause]", "zen"),
            ("Your chest and upper back. Let your shoulders drop away from your ears.", "meditate"),
            ("[pause]", "zen"),
            ("Your arms and hands. Soften your fingers. Let them be still.", "meditate"),
            ("[pause]", "zen"),
            ("Your neck and throat. Swallow once and let everything relax.", "meditate"),
            ("[pause]", "zen"),
            ("Your face. Unclench your jaw. Soften your eyes. Let your forehead be smooth.", "meditate"),
            ("[pause]", "zen"),
            ("Your whole body now. From toes to the top of your head. One complete, living, breathing whole.", "meditate"),
            ("[pause]", "zen"),
            ("Rest here for a moment. Nothing to do. Nowhere to be.", "zen"),
            ("[pause]", "zen"),
            ("When you're ready, wiggle your fingers and toes. Gently open your eyes.", "meditate"),
            ("Welcome back. Take this calm with you.", "gentle"),
        ],
        "suggested_duration_min": 5,
    },
    "loving-kindness": {
        "name": "Loving-Kindness (Metta)",
        "description": (
            "A traditional Buddhist practice of directing well-wishes toward "
            "yourself and others. Backed by research on increasing positive emotions."
        ),
        "script": [
            ("Sit comfortably. Close your eyes. Hand on your heart if that feels right.", "meditate"),
            ("Take a few deep breaths. Let your heart area feel warm.", "breathing_in"),
            ("[pause]", "zen"),
            ("Now, silently repeat these phrases toward yourself:", "meditate"),
            ("May I be happy.", "gentle"),
            ("May I be healthy.", "gentle"),
            ("May I be safe.", "gentle"),
            ("May I live with ease.", "gentle"),
            ("[pause]", "zen"),
            ("Don't worry if it feels awkward. That's normal. Just let the words be there.", "meditate"),
            ("[pause]", "zen"),
            ("Now bring to mind someone you love easily. A friend, a pet, a kind mentor.", "meditate"),
            ("Picture them. Feel the warmth of your connection.", "gentle"),
            ("May you be happy.", "gentle"),
            ("May you be healthy.", "gentle"),
            ("May you be safe.", "gentle"),
            ("May you live with ease.", "gentle"),
            ("[pause]", "zen"),
            ("Now bring to mind a neutral person. Someone you see but don't know well.", "meditate"),
            ("The barista. The neighbor you nod at. The person who delivers your mail.", "meditate"),
            ("They want to be happy too. Just like you.", "gentle"),
            ("May you be happy. May you be healthy. May you be safe. May you live with ease.", "gentle"),
            ("[pause]", "zen"),
            ("Now — if it feels right — bring to mind someone you have difficulty with.", "meditate"),
            ("Just for a moment. They're human too. They struggle too.", "concerned"),
            ("May you be happy. May you be healthy. May you be safe. May you live with ease.", "gentle"),
            ("[pause]", "zen"),
            ("Finally, expand to all beings everywhere.", "meditate"),
            ("May all beings be happy. May all beings be healthy. May all beings be safe. May all beings live with ease.", "gentle"),
            ("[pause]", "zen"),
            ("Sit with that feeling. This warmth you generated — it came from you.", "proud"),
            ("When you're ready, open your eyes.", "meditate"),
        ],
        "suggested_duration_min": 8,
    },
    "just-sit": {
        "name": "Just Sitting",
        "description": (
            "No technique. No goal. Just being here. A minimalist approach "
            "to meditation — sometimes the hardest and most rewarding."
        ),
        "script": [
            ("Sit comfortably. Spine upright but not rigid.", "meditate"),
            ("Close your eyes. Or keep them open, soft-focused on the floor in front of you.", "meditate"),
            ("[pause]", "zen"),
            ("There's nothing to do right now. Nothing to achieve.", "meditate"),
            ("Thoughts will come. That's fine. They're supposed to.", "meditate"),
            ("When you notice you're thinking, just note: 'thinking.'", "thoughtful"),
            ("Then return to the breath. Or the sounds in the room. Or the feeling of sitting.", "meditate"),
            ("[pause]", "zen"),
            ("No judgment. No 'I'm doing this wrong.' There is no wrong.", "gentle"),
            ("[pause]", "zen"),
            ("If you get lost in thought a hundred times, just return a hundred times.", "meditate"),
            ("Each return is the practice. Each return is a tiny victory.", "encourage"),
            ("[pause]", "zen"),
            ("Just this. Just sitting. Just breathing. Just being.", "zen"),
            ("[pause]", "zen"),
            ("When you're ready, take a deeper breath. Notice how you feel.", "meditate"),
            ("Gently open your eyes. Carry this simplicity with you.", "gentle"),
        ],
        "suggested_duration_min": 5,
    },
}


def get_meditation_script(style: str) -> Optional[Dict]:
    """Get a meditation script by style name."""
    return MEDITATION_SCRIPTS.get(style)


def list_styles() -> List[str]:
    """Return available meditation style names."""
    return [
        {"name": s["name"], "duration_min": s["suggested_duration_min"]}
        for s in MEDITATION_SCRIPTS.values()
    ]


def get_phrases(style: str, count: Optional[int] = None) -> List[tuple]:
    """
    Get meditation phrases for step-by-step display.

    Args:
        style: 'body-scan', 'loving-kindness', or 'just-sit'
        count: Optional max number of phrases to return

    Returns:
        List of (text, mood) tuples
    """
    meditation = MEDITATION_SCRIPTS.get(style)
    if meditation is None:
        return [("Sit quietly and breathe. Just be here.", "meditate")]

    script = meditation["script"]
    if count:
        script = script[:count]

    return script
