# Build Small Hackathon — Submission Drafts

## 🐾 CritterCalm — Social Post (Twitter/X)

```
I built something for my dog's separation anxiety.

🐾 CritterCalm clones your voice (from just 3 seconds of audio)
and generates calming audio sessions tailored to YOUR specific pet.

Dogs. Cats. Chickens. Horses. Rabbits. Birds.

All running 100% locally. No cloud. No data collection.

🧠 OmniVoice (0.6B) — zero-shot voice cloning
💬 Dolphin-X1-8B — calming script generation
🎤 Kokoro TTS (82M) — built-in soothing voices

Total: ~8.7B params, runs on a laptop.

Built for the @huggingface #BuildSmallHackathon — Backyard AI track.

🔗 GitHub: github.com/nbiish/crittercalm
🤗 Space: huggingface.co/spaces/build-small-hackathon/crittercalm

Try it. Your anxious pup will thank you. 🐕💚
```

---

## ✦ FocusFriend — Social Post (Twitter/X)

```
I built an AI friend who lives in a terminal window.

He's called Pip. He's an ASCII character. He won't give you
toxic positivity or corny motivational quotes.

What Pip WILL do:
🎯 Keep you focused (Pomodoro with sass)
🌬️ Guide your breathing (actual techniques, not "just relax")
🧘 Lead short meditations (body scan, loving-kindness)
💬 Talk to you like a real friend who's been to therapy

Pip's personality: dry-witted, warm, psychologically authentic.
"You're not your thoughts. You're the one watching them.
Also, your posture is terrible. Let's fix that."

12B params (Gemma 4). Runs fully local.
Custom dark UI. 18 ASCII expressions.

Built for @huggingface #BuildSmallHackathon — Thousand Token Wood track.

🔗 GitHub: github.com/nbiish/focusfriend
🤗 Space: huggingface.co/spaces/build-small-hackathon/focusfriend

Come meet Pip. He's weird. You'll like him. ✦
```

---

## 📝 Field Notes — Blog Post: CritterCalm

### How I Built an AI Voice Cloner to Calm Anxious Pets (and What I Learned About Animal Psychoacoustics)

**The Problem**

My neighbor Sarah has a rescue pitbull named Gus. Gus is the sweetest dog — until Sarah leaves for work. Then the howling starts. The pacing. The destroyed couch cushions. She's tried everything: white noise machines, treat puzzles, ThunderShirts, even leaving the TV on. Nothing works consistently.

The thing is, Gus isn't anxious because he's alone. He's anxious because *Sarah* isn't there. Research shows dogs process their owner's voice in the same brain regions humans use for face recognition. Your voice literally lights up their brain like a familiar face lights up yours.

So I thought: what if Sarah could leave her *voice* with Gus?

**The Build**

The Build Small Hackathon gave me 10 days and a 32-billion-parameter budget. Here's what I stacked:

1. **OmniVoice (0.6B)** — Xiaomi's open-source voice cloning model. 646 languages, zero-shot cloning from 3 seconds of audio, Apache 2.0. It's absurdly good for its size.

2. **Dolphin-X1-8B (8B)** — A steerable Llama 3.1 derivative that generates species-appropriate calming scripts. Dogs need short, rhythmic reassurance. Cats need slow, soft cadence with blink references. Chickens need flock-safety messaging. Each animal has a completely different psychoacoustic profile.

3. **Kokoro TTS (82M)** — A tiny fallback TTS for built-in soothing voices when cloning isn't available.

The whole stack runs on a laptop. No cloud. No API calls. No data leaving the device.

**What I Learned About Animal Psychoacoustics**

This was the surprising part. I went deep on the research while building the calming scripts:

- Dogs respond to prosody (the musical quality of speech) more than words. Short phrases, descending pitch, steady rhythm.
- Cats show measurable cortisol reduction when hearing their owner's voice — but only in "cat-directed speech" (higher pitch, slower tempo).
- Chickens recognize individual human voices and show fewer alarm calls with familiar, calm speech.
- Horses' heart rates drop measurably when hearing a familiar human voice during stress.

The species-specific templates ended up being the most important part of the app. The AI voice cloning is the magic trick — but the *content* of what you say to each animal is where the science lives.

**What I'd Do Differently**

- Fine-tune OmniVoice on pet-directed speech (the "baby voice" people use with their pets has different acoustic properties)
- Add real-time microphone input so the app listens for animal distress vocalizations and responds
- Build a hardware version for a Raspberry Pi that sits in the pet's room

**Try It**

The app is a Gradio Space. Record 10 seconds of your voice, pick your pet type and situation, and it generates a personalized calming audio session. It's not a replacement for training or veterinary care — but it's a tool that uses real science to strengthen the bond between pets and their people.

---

## 📝 Field Notes — Blog Post: FocusFriend

### I Built an ASCII Character Who Became My Wellness Companion (and Why It's Not as Weird as It Sounds)

**The Concept**

Wellness apps are terrible.

They're either saccharine cheerleaders ("You're AMAZING! 🌟") or sterile productivity machines ("Session 3 of 8 complete. Efficiency: 87%."). Neither feels human. Neither actually helps when you're stuck, anxious, or just tired.

So I built Pip.

Pip is an ASCII character who lives in a Gradio window. He has 18 facial expressions. He talks to you like a friend who's been through therapy — dry-witted, psychologically informed, and completely allergic to toxic positivity.

**The Personality Design**

The hardest part wasn't the code. It was the voice.

How do you make an AI character feel genuinely supportive without being corny? How do you express care without veering into "I'm a Large Language Model and I'm here to help!" territory?

I wrote a 500-word system prompt that defines Pip's entire personality:

- Dry-witted and slightly mischievous
- Wise — like a friend who actually listened in therapy
- Action-oriented: suggests things, doesn't just offer sympathy
- Concise: 2-5 sentences max, unless guiding a meditation
- Honest about being AI: "I'm about as conscious as a really well-written to-do list"

The breakthrough was the mood system. Every response Pip gives includes a [mood: ___] tag. The frontend parses this and displays the matching ASCII expression. When Pip is concerned, his eyebrows furrow. When he's celebrating with you, his eyes become stars. When he's guiding breathing, he breathes with you.

**The Tech**

- **Gemma 4 12B** via llama.cpp — Google's newest open model, running locally at Q4_K_M quantization (~7.7GB)
- **Gradio** with a fully custom CSS theme (dark background, amber accents, monospace Pip)
- **Custom JavaScript** for the breathing animation timer and focus countdown
- **Fallback system**: When the model isn't loaded, Pip still works using pre-written responses

The entire thing runs offline. Your conversations never leave your laptop.

**The Four Modes**

1. **Focus (Pomodoro)**: Pip checks in, then stays quiet. He's keeping time. You're doing the work. At the end, a genuine "nice job" — not a confetti cannon.

2. **Breathe**: 4-7-8 breathing, box breathing, or simple deep breathing. Pip's ASCII face literally breathes with you. The JavaScript animates his expression through inhale, hold, and exhale phases.

3. **Meditate**: Body scan, loving-kindness (metta), or "just sitting." Pre-written scripts guided by Pip's calming presence. No AI generation needed — these are timeless practices.

4. **Chat**: Open conversation. Pip remembers context. He notices patterns. "Hey, you've been at this for 3 hours. Your eyes are probably drier than a PowerPoint presentation. Let's fix that."

**What Surprised Me**

People who tested it *liked* that Pip isn't always positive. The gentle pushback — "You said that yesterday. How'd it actually go?" — felt more supportive than unconditional praise.

The ASCII art mattered more than I expected. Seeing Pip's expression change in response to what you say creates a weirdly compelling sense of presence. It's not a person. But it's not nothing, either.

**Try It**

Pip lives at the Hugging Face Space linked below. He's weird. He's small. He genuinely wants you to feel better — not because he's programmed to, but because that's the kind of character he turned out to be.

Sometimes the best wellness tools aren't the shiniest. Sometimes they're just a tiny ASCII friend who looks at you with dot eyes and says "Yeah, that IS hard. Let's deal with it."

---

## 🏅 Bonus Quest Checklist

| Badge | CritterCalm | FocusFriend |
|-------|-------------|-------------|
| 🔌 Off the Grid | ✅ All local, no APIs | ✅ All local, no APIs |
| 🎯 Well-Tuned | ⬜ Fine-tune OmniVoice | N/A |
| 🎨 Off-Brand | ⬜ | ✅ Custom CSS/JS dark theme |
| 🦙 Llama Champion | ⬜ | ⬜ (using llama.cpp, need to flag) |
| 📡 Sharing is Caring | ⬜ Share agent traces | ⬜ Share agent traces |
| 📓 Field Notes | ✅ Draft written | ✅ Draft written |
| 🏆 Tiny Titan | N/A (8.7B total) | ⬜ (12B Gemma, could offer 1.5B option) |

---

## 🚀 Deploy to Hugging Face Spaces

```bash
# 1. Login to Hugging Face
huggingface-cli login
# OR: hf auth login

# 2. Create Spaces (via web UI or CLI)
# Go to: https://huggingface.co/new-space
# Organization: build-small-hackathon
# Space name: crittercalm  (and: focusfriend)
# SDK: Gradio
# Then push:

# CritterCalm
cd /Volumes/1tb-sandisk/code-external/crittercalm-repo
git remote add hf https://huggingface.co/spaces/build-small-hackathon/crittercalm
git push hf main

# FocusFriend
cd /Volumes/1tb-sandisk/code-external/focusfriend-repo
git remote add hf https://huggingface.co/spaces/build-small-hackathon/focusfriend
git push hf main
```
