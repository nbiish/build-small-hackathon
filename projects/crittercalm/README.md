---
title: CritterCalm
emoji: 🐾
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - voice-cloning
  - tts
  - pets
  - animals
  - backyard-ai
  - build-small-hackathon
  - local-first
  - off-the-grid
---

# 🐾  CritterCalm — AI Voice Cloning Animal Soother

**Clone your voice. Calm your pets.**

CritterCalm clones your voice using state-of-the-art open-source AI, then generates
personalized calming audio sessions for your pets. Dogs, cats, chickens, birds,
rabbits, horses — every animal responds to their person's voice.

## ✨  Features

- **🎤  Voice Cloning** — Clone your voice from just 3-10 seconds of audio
- **🐕  Multi-Animal Support** — Species-specific calming techniques for 6 animal types
- **🎯  Situation-Aware** — Tailored scripts for anxiety, storms, vet visits, and more
- **🔌  100% Local** — No cloud APIs, no data collection, fully offline
- **📚  Science-Backed** — Based on animal cognition and psychoacoustics research

## 🚀  Quick Start

```bash
# Clone and install
git clone <this-repo>
cd crittercalm
pip install -r requirements.txt

# Download models (first run will auto-download from Hugging Face)
python app.py
```

## 🧠  Model Stack

| Model | Size | Purpose | License |
|-------|------|---------|---------|
| OmniVoice | 0.6B | Voice cloning + TTS | Apache 2.0 |
| Dolphin-X1-8B | 8B | Calming script generation | Llama 3.1 |
| Kokoro TTS | 82M | Built-in soothing voices (fallback) | Apache 2.0 |

**Total: ~8.7B params** (well under the 32B limit)

## 🏅  Hackathon Track

**Backyard AI** — Solving a real problem for real pet owners.

### Bonus Badges
- 🔌  **Off the Grid** — Fully local, no API calls
- 🎯  **Well-Tuned** — Fine-tuned voice embeddings for pet-directed speech
- 📓  **Field Notes** — Blog post on animal psychoacoustics + voice cloning

## 📁  Project Structure

```
crittercalm/
├── app.py                 # Main Gradio application
├── voice_cloning/         # OmniVoice integration
├── content/               # Script generation + templates
├── utils/                 # Audio processing utilities
├── requirements.txt
└── README.md
```

## 🤝  Credits

Built with ❤️ for the Build Small Hackathon 2026.
