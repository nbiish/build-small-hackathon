"""
Breathing exercise mode for FocusFriend.

Pip guides you through breathing techniques:
- 4-7-8 breathing (relaxation)
- Box breathing (focus/calm)
- Simple deep breathing (general wellness)
"""

from typing import Dict, List, Tuple, Optional

# Breathing technique definitions
# Each has: name, description, phases with (duration_sec, instruction, pip_mood)

BREATHING_TECHNIQUES: Dict[str, Dict] = {
    "4-7-8": {
        "name": "4-7-8 Breathing",
        "description": (
            "Developed by Dr. Andrew Weil. Activates the parasympathetic "
            "nervous system — your body's 'rest and digest' mode."
        ),
        "rounds": 4,
        "phases": [
            (4, "Inhale quietly through your nose …", "breathing_in"),
            (7, "Hold your breath …", "breathing_hold"),
            (8, "Exhale completely through your mouth, making a whoosh sound …", "breathing_out"),
        ],
        "prelude": (
            "Get comfortable. Rest your tongue gently against the roof of your mouth, "
            "just behind your front teeth. You'll exhale around it."
        ),
        "benefits": [
            "Reduces anxiety",
            "Helps with falling asleep",
            "Lowers heart rate",
            "Manages craving responses",
        ],
    },
    "box": {
        "name": "Box Breathing",
        "description": (
            "Used by Navy SEALs, first responders, and anyone who needs to stay "
            "calm under pressure. Also called 'square breathing.'"
        ),
        "rounds": 4,
        "phases": [
            (4, "Inhale slowly through your nose …", "breathing_in"),
            (4, "Hold … steady …", "breathing_hold"),
            (4, "Exhale slowly through your nose …", "breathing_out"),
            (4, "Hold … empty and calm …", "breathing_hold"),
        ],
        "prelude": (
            "Sit up straight. Hands on your thighs. "
            "Visualize drawing a square: up, across, down, across."
        ),
        "benefits": [
            "Acute stress relief",
            "Improves focus and concentration",
            "Calms the nervous system",
        ],
    },
    "simple": {
        "name": "Simple Deep Breathing",
        "description": (
            "No counting, no technique — just deep, conscious breathing. "
            "Sometimes the simplest approach is the most effective."
        ),
        "rounds": 6,
        "phases": [
            (4, "Breathe in … slow and deep …", "breathing_in"),
            (6, "Breathe out … letting everything go …", "breathing_out"),
        ],
        "prelude": (
            "Close your eyes. One hand on your chest, one on your belly. "
            "Feel the breath move through you."
        ),
        "benefits": [
            "Accessible to everyone",
            "Can be done anywhere",
            "Builds breath awareness",
            "Good starting point for beginners",
        ],
    },
}


def get_technique(name: str) -> Optional[Dict]:
    """Get a breathing technique by name. Supports '4-7-8', 'box', 'simple'."""
    # Normalize
    key = name.lower().replace(" ", "").replace("-", "")
    if key in ("478", "4-7-8", "4_7_8"):
        key = "4-7-8"
    return BREATHING_TECHNIQUES.get(key)


def list_techniques() -> List[str]:
    """Return names of available breathing techniques."""
    return [t["name"] for t in BREATHING_TECHNIQUES.values()]


def get_breathing_guide(technique_name: str, round_num: int, phase_num: int) -> Tuple[str, str]:
    """
    Get the instruction and mood for a specific phase of a breathing round.

    Args:
        technique_name: '4-7-8', 'box', or 'simple'
        round_num: 0-based round index
        phase_num: 0-based phase index within the round

    Returns:
        (instruction_text, pip_mood) tuple
    """
    technique = get_technique(technique_name)
    if technique is None:
        return "Breathe naturally. Just notice your breath.", "meditate"

    phases = technique["phases"]
    phase = phases[phase_num % len(phases)]
    duration, instruction, mood = phase

    return instruction, mood


def generate_breathing_script(technique_name: str) -> List[Dict]:
    """
    Generate a full breathing exercise script.

    Returns:
        List of dicts: {phase, duration_sec, instruction, mood}
    """
    technique = get_technique(technique_name)
    if technique is None:
        return []

    script = []
    for round_num in range(technique["rounds"]):
        for phase_num, phase in enumerate(technique["phases"]):
            duration, instruction, mood = phase
            script.append({
                "round": round_num + 1,
                "phase": phase_num + 1,
                "total_phases": len(technique["phases"]),
                "duration_sec": duration,
                "instruction": instruction,
                "mood": mood,
            })

    return script
