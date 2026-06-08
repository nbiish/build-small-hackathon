"""
Pre-written calming scripts for when the LLM is unavailable.
Each template is species-appropriate and situation-specific.
"""

from typing import Optional


TEMPLATES: dict[str, dict[str, str]] = {
    "Dog": {
        "Separation Anxiety": (
            "Hey there, sweet pup. I know it's hard when I leave, but I'm always coming back. "
            "Right now, you're safe in your favorite spot. Feel the soft blanket under your paws — "
            "that's your spot, your safe place. Take a deep, slow breath and let your ears relax. "
            "Remember this morning when we played together? That was fun. We'll play again soon. "
            "For now, just rest. You're such a good dog. The best dog. "
            "I love you more than all the treats in the world. Shhh … settle down now. "
            "I'll be home before you know it. Sweet dreams, my good pup."
        ),
        "Thunderstorm / Fireworks": (
            "Hey buddy, I'm here with you. I know those loud sounds are scary. "
            "But you're inside, you're safe, and nothing can hurt you here. "
            "Feel the floor under you — solid, steady, peaceful. "
            "Those booms outside? They're just noise. They come and they go, but you and me? "
            "We're constant. We're together in spirit. Lean into your bed, let your weight sink down. "
            "Good dog. Brave dog. This storm will pass, like all storms do. "
            "I'm right here with you, breathing slow. Breathe with me. In … and out … "
            "Good. That's perfect. You're safe."
        ),
        "Vet Visit": (
            "Alright sweetheart, I know this place smells funny. All those other animal smells — "
            "I get it. But these people? They're helpers. They want you to feel good. "
            "Remember the last time we were here, and you got that tasty treat after? "
            "We're going to do this together. I'm right beside you. "
            "You're being so brave right now. The bravest pup in the whole place. "
            "Just a little checkup, and then we go home. Maybe we stop for a pup-cup on the way? "
            "Yeah, you'd like that. Good dog. The best dog. We're almost done."
        ),
        "General Calm": (
            "Hey there, my good pup. Let's just settle in together. "
            "Feel how calm this moment is. Nothing to worry about, nothing to chase. "
            "Just you and me, breathing easy. You've had a good day — "
            "walks and belly rubs and maybe a treat or two. Now it's time to rest. "
            "Rest your head. Let your eyes get heavy. You're safe, you're loved, "
            "and you're the best companion anyone could ask for. "
            "Good night, sweet pup. Sweet dreams."
        ),
        "Bedtime": (
            "It's that time, sweet friend. The day is done, the stars are out, "
            "and it's time to curl up and drift away. Find your coziest spot — "
            "yes, that one. Curl up nice and tight. Feel your breathing slow down. "
            "Think of all the good things today: the sunshine, the treats, the belly rubs. "
            "Tomorrow there will be more. But for now, just sleep. "
            "I'm right here. I'll be here when you wake up. Sweet dreams, my good pup. "
            "Sleep well."
        ),
        "Travel / Car Ride": (
            "Hey buddy, we're going on an adventure. I know the car feels different — "
            "all that motion and those passing sounds. But look: I'm right here next to you. "
            "We're going somewhere good together. Every turn of the wheels brings us closer. "
            "Just settle into your spot. Watch the world go by if you want, or just close your eyes. "
            "We're safe, we're together, and this is just another little journey. "
            "Good dog. Travel buddy. We'll be there soon."
        ),
        "New Environment": (
            "Okay, I know — new place, new smells, new everything. It's a lot to take in. "
            "But look at me: I'm here. This new place has us in it, which makes it ours. "
            "Let's explore together, one sniff at a time. Take your time. "
            "There's no rush. Everything unfamiliar will become familiar. "
            "You've got this. I've got you. We're a team."
        ),
        "Loud Noises": (
            "Hey hey hey — I hear it too. That's a loud one. "
            "But we're inside, we're together, and it's just noise. "
            "Noise can't touch us. Come closer if you need to. "
            "Feel my hand on your fur. Steady. Steady. "
            "The noise is already fading. You're still here, still safe, still loved. "
            "Good pup. Brave pup. Everything's okay."
        ),
    },
    "Cat": {
        "Separation Anxiety": (
            "Hello, my elegant friend. I know you miss me when I'm gone — "
            "I miss you too. But this is your kingdom, and you are its ruler. "
            "The sunny spot on the windowsill is yours. The soft blanket is yours. "
            "Stretch out in that patch of sunlight and feel the warmth soak into your fur. "
            "You're not alone — you're in your domain. Every corner holds our memories. "
            "I'll be back soon, and we'll have our evening ritual. "
            "Until then, reign in peace, my little monarch. Purr for me."
        ),
        "Thunderstorm / Fireworks": (
            "Shhh, little one. I hear it — those loud cracks in the sky. "
            "But you're clever. You know they can't reach you here. "
            "Slide under your favorite hiding spot if you want. That's your secret fortress. "
            "Nothing gets in unless you allow it. Feel how steady the floor is? "
            "That steadiness is yours. Let your whiskers relax. "
            "Let your tail uncurl. The storm is just passing through — it doesn't live here. "
            "You do. You're safe. You're the guardian of this space."
        ),
        "Vet Visit": (
            "Alright, my dignified companion. I know the carrier is undignified. "
            "I know this place has all those … other cat smells. How gauche. "
            "But we conduct ourselves with grace, don't we? These people are just doing their jobs. "
            "You'll endure their poking and prodding with the quiet superiority of a cat "
            "who knows they're above all this. And after? Home. Treats. "
            "The best spot on the couch, uninterrupted. You've earned it."
        ),
        "General Calm": (
            "Oh, magnificent creature. Look at you — the picture of feline contentment. "
            "Your whiskers are at ease. Your tail is curled just so. "
            "This moment is yours. The soft hum of the house, the gentle light through the window — "
            "all of it arranged for your comfort. Take a long, slow blink. "
            "That's a smile in cat language, you know. I'm smiling back. "
            "Rest now, little lion. Your kingdom is peaceful."
        ),
        "Bedtime": (
            "The house is settling, little one. The birds outside have gone to their nests. "
            "Find your spot — that perfect curl of warmth. Tuck your paws in. "
            "Let your purr be your lullaby. Tomorrow the sun will return, "
            "and with it the birds to watch and the warm spots to lounge in. "
            "But tonight, just sleep. I'll guard your dreams. "
            "Good night, sweet cat."
        ),
        "Travel / Car Ride": (
            "I know, I know — the carrier. The motion. Very undignified. "
            "But consider: every mile brings us closer to home again. Or perhaps to somewhere new and interesting. "
            "You're safe in there, even if it doesn't feel like it. "
            "The hum of the engine is just a mechanical purr. "
            "Close your eyes and pretend it's me. We'll be still again soon."
        ),
        "New Environment": (
            "A new realm to conquer, my little explorer. I understand — "
            "it smells wrong. The furniture is in the wrong places. "
            "But you are a cat, the most adaptable of creatures. "
            "By tomorrow, this will be yours. Find the highest perch. Claim it. "
            "Everything else will follow. I'm here with you while you survey your new domain."
        ),
        "Loud Noises": (
            "I hear it. You hear it. But we are cats in spirit — "
            "above such things. Find your fortress. Under the bed, behind the couch — "
            "you know all the best spots. Settle in there and let the noise be outside. "
            "It can't enter your sanctuary. You're safe in your chosen fortress. "
            "I'll keep watch. You just be a cat."
        ),
    },
    "Chicken": {
        "Separation Anxiety": (
            "Bawk bawk, sweet feather-bundle. The flock is nearby — you're not alone. "
            "Feel the warm earth under your feet. Scratch a little if you want. "
            "There are good things in this dirt — seeds and grubs and little treasures. "
            "The sun is warm on your back. The coop is safe. "
            "Listen: the other hens are clucking softly. They're your sisters. "
            "Settle into the dust bath. Let your feathers fluff. "
            "All is well in the chicken yard. All is well."
        ),
        "Thunderstorm / Fireworks": (
            "Easy, feathered friend. The sky is making noise, but the coop is strong. "
            "Tuck in close to the others. Feel their warmth — that's flock warmth. "
            "That's safety. The roof holds. The walls stand. "
            "Nothing can reach you in here. The rumbling will pass, as it always does. "
            "Close your bright eyes. Tuck your head under your wing. "
            "The flock is together. The flock is safe."
        ),
        "General Calm": (
            "Good morning, lovely hen. The sun is up and the coop door is open. "
            "What a beautiful day for scratching and pecking. "
            "The grass is dewy, the bugs are slow, and the dirt is perfect for dust baths. "
            "Stretch your wings in the sun — feel that warmth soak into your feathers. "
            "You're a good chicken. The best chicken. Lay your egg in the nesting box "
            "and strut with pride. You've earned it."
        ),
        "Bedtime": (
            "The sun is going down, little hen. Time to find your spot on the roost. "
            "Settle in next to your sisters. Feel their feathers against yours — "
            "that's flock warmth. That's home. The day was full of good scratches "
            "and tasty bugs. Tomorrow brings more. But for now, tuck your head "
            "under your wing and rest. The roost is safe. The night is calm. "
            "Good night, feathered friend."
        ),
    },
    "Bird": {
        "Separation Anxiety": (
            "Hello, bright eyes. I see you there on your perch. "
            "You're not alone — look around your cage. Your toys, your mirror, your bell — "
            "all familiar, all yours. Why don't you give that bell a little ring? "
            "That's your song. Your voice. Sing it out, and I'll hear it in my heart. "
            "I'll be back with millet and gentle words. Until then, chirp your song. "
            "You're such a good bird."
        ),
        "Thunderstorm / Fireworks": (
            "Easy, bright one. Those sounds are big, but you're safe in your cage. "
            "The bars are sturdy, the cover is near if you want darkness. "
            "Take a little seed. Crack it slowly. Focus on that — "
            "the tiny task of eating, of being a bird, of being safe. "
            "The sky-show will pass. You'll still be here, on your perch, "
            "ready to sing when it's over."
        ),
        "General Calm": (
            "Hello, my feathered musician. What a beautiful day to sing. "
            "Your cage is clean, your water is fresh, and that millet spray looks particularly good today. "
            "Preen your feathers — make them shine. You're safe here, surrounded by your things. "
            "Whistle a little tune. I'll whistle back. We're a duet, you and me."
        ),
        "Bedtime": (
            "Time to settle, little singer. The sun has gone and the world is quiet. "
            "Fluff up your feathers. Tuck your beak into your wing. "
            "Today you sang, you played, you were a good bird. "
            "Tomorrow you'll do it all again. But now — "
            "sleep. The cage cover is drawn. The room is still. "
            "Sweet dreams, feathered friend."
        ),
    },
    "Rabbit": {
        "Separation Anxiety": (
            "Hello, soft one. I know you miss me, but you're in your burrow — "
            "your safe, cozy space. The hay is fresh and smells of summer fields. "
            "Give it a little nibble. Feel the crunch, the sweetness. "
            "Your hidey-hole is warm and dark, just the way you like it. "
            "Stretch out your back legs and let your ears relax. "
            "I'll be back with fresh greens before you know it. Rest now, little bun."
        ),
        "Thunderstorm / Fireworks": (
            "Shh, little hopper. I hear it too. But your burrow is deep and safe. "
            "The walls are solid. The hay is thick. Nothing from outside can find you here. "
            "Thump once if you need to — let it out. Good. Now settle. "
            "Your nose can stop twitching so fast. Slow twitches. "
            "Slow breaths. The danger isn't here. You're in your sanctuary."
        ),
        "General Calm": (
            "Hello, cotton-tail. Look at you, lounging in your favorite spot. "
            "Your nose is twitching at a leisurely pace — that's a good sign. "
            "Why not flop over on your side? Yes, that's the bunny way. "
            "Feet out. Ears relaxed. You're safe and loved and you have unlimited hay. "
            "What more could a rabbit want? Rest easy, little friend."
        ),
        "Bedtime": (
            "The hutch is quiet, little bun. The night is cool and calm. "
            "Tuck into your favorite corner — the one with the softest hay. "
            "Today you hopped and explored and nibbled to your heart's content. "
            "Now it's time to dream bunny dreams — fields of clover, warm sunshine, "
            "all the dandelion leaves you could ever want. Sleep well, soft one."
        ),
    },
    "Horse": {
        "Separation Anxiety": (
            "Easy, big friend. I know the barn feels different when I'm not there. "
            "But listen — you can hear the other horses. Jasper is in his stall. "
            "Luna is munching hay. They're your herd. They're here. "
            "Take a deep breath — fill those big lungs all the way. "
            "Now let it out slow, like you're blowing on a dandelion. "
            "Good. Again. I'll be back for our ride soon. Until then, "
            "you've got hay, you've got water, you've got your herd. "
            "Stand easy, my noble friend."
        ),
        "Thunderstorm / Fireworks": (
            "Steady now. Steady. I hear the thunder too. "
            "It's loud, but it's far away. This barn has stood through a hundred storms, "
            "and it'll stand through a hundred more. You're inside, you're dry, "
            "and the hay in your rack tastes just the same as it did before the storm. "
            "Drop your head a little. Let your neck relax. "
            "There you go. The storm has no power over you. You're too big, too strong, "
            "too grounded for it to touch. Steady."
        ),
        "General Calm": (
            "Hello there, beautiful. The sun is warm on your back and the pasture is quiet. "
            "Take a deep, slow breath and let your muscles soften — "
            "let go of that tension in your withers, your neck, your haunches. "
            "The grass is sweet today, isn't it? You've earned this peaceful moment. "
            "No rides, no work — just being a horse in a sunny field. "
            "You're magnificent. You're loved."
        ),
        "Bedtime": (
            "The barn is settling into darkness, my friend. "
            "The last hay has been fed, the water troughs are full. "
            "The night birds are starting their songs. "
            "Rest one hind leg — let it cock just so. That's your relaxation posture. "
            "Your herd is dozing around you. The night watch has begun. "
            "Sleep standing tall, noble one. Tomorrow the pasture waits. "
            "Good night."
        ),
    },
}


def get_template(
    animal: str,
    situation: str,
    pet_name: str = "",
    custom_message: str = "",
) -> str:
    """
    Return a pre-written calming script for the given animal and situation.

    Args:
        animal: One of Dog, Cat, Chicken, Bird, Rabbit, Horse
        situation: The stress situation
        pet_name: Optional pet name to sprinkle into the script
        custom_message: Optional custom message to prepend

    Returns:
        A calming script string
    """
    animal_templates = TEMPLATES.get(animal)
    if animal_templates is None:
        animal_templates = TEMPLATES["Dog"]  # fallback

    script = animal_templates.get(
        situation,
        animal_templates.get("General Calm", "You're safe and loved, sweet friend."),
    )

    # Inject pet name if provided
    if pet_name.strip():
        # Replace generic "sweet pup", "my good pup", etc. with the name
        script = script.replace("sweet pup", pet_name)
        script = script.replace("good pup", pet_name)
        script = script.replace("my good pup", pet_name)
        script = script.replace("sweet friend", pet_name)
        # Add name to the beginning
        if not script.startswith(pet_name):
            script = f"{pet_name}, " + script[0].lower() + script[1:]

    # Prepend custom message
    if custom_message.strip():
        script = f"{custom_message.strip()}\n\n{script}"

    return script


def list_animals() -> list[str]:
    """Return supported animal types."""
    return list(TEMPLATES.keys())


def list_situations(animal: str) -> list[str]:
    """Return available situations for a given animal type."""
    animal_templates = TEMPLATES.get(animal, {})
    return list(animal_templates.keys())


def has_template(animal: str, situation: str) -> bool:
    """Check if a specific template exists."""
    return animal in TEMPLATES and situation in TEMPLATES[animal]
