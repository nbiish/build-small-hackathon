"""
Calming script generation using Dolphin-X1-8B (via llama.cpp) or templates.

Provides:
- generate_calming_script(): LLM-based generation with template fallback
- CALMING_SYSTEM_PROMPT: The system prompt for Dolphin
- create_script_prompt(): Build the user prompt for script generation
"""

import logging
from content.templates import get_template

log = logging.getLogger("crittercalm.content")

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


def create_script_prompt(
    animal: str,
    situation: str,
    duration_minutes: int,
    pet_name: str = "",
    custom_message: str = "",
) -> str:
    """
    Build the user prompt for the LLM to generate a calming script.

    Args:
        animal: Animal type (Dog, Cat, Chicken, etc.)
        situation: The stress situation
        duration_minutes: Target session length in minutes
        pet_name: Optional pet name
        custom_message: Optional custom message to include

    Returns:
        Formatted prompt string
    """
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

    return (
        f"Write a calming spoken message for a {animal} {name_clause}.\n"
        f"Situation: {situation}.\n"
        f"Length: {duration_words}.{custom_clause}\n"
        f"Make it warm, soothing, and specifically tailored to a {animal}'s needs."
    )


def generate_calming_script(
    animal: str,
    situation: str,
    duration_minutes: int,
    custom_message: str = "",
    pet_name: str = "",
    dolphin_llm=None,
) -> str:
    """
    Generate a calming script using Dolphin-X1-8B or fallback templates.

    Args:
        animal: Animal type
        situation: Stress situation
        duration_minutes: Target session length
        custom_message: Optional custom message
        pet_name: Optional pet name
        dolphin_llm: Optional pre-loaded llama_cpp.Llama instance

    Returns:
        Generated calming script as a string
    """
    prompt = create_script_prompt(
        animal=animal,
        situation=situation,
        duration_minutes=duration_minutes,
        pet_name=pet_name,
        custom_message=custom_message,
    )

    # Try LLM generation
    if dolphin_llm is not None:
        try:
            response = dolphin_llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": CALMING_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
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
    return get_template(animal, situation, pet_name, custom_message)
