---
title: FocusFriend
emoji: ✦
colorFrom: indigo
colorTo: amber
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - wellness
  - ascii-art
  - meditation
  - focus
  - thousand-token-wood
  - build-small-hackathon
  - local-first
  - off-the-grid
  - tiny-titan
---

# ✦  FocusFriend — Pip, Your ASCII Wellness Companion

**A tiny ASCII character who genuinely wants you to feel better.**

Pip is a wise, dry-witted, slightly mischievous but genuinely caring wellness
companion. Not a sycophantic cheerleader. Think: "your friend who's been through
therapy and wants you to actually feel better, not just hear platitudes."

## ✨  Features

- **💬  Chat Mode** — Talk to Pip. Real conversation, no corny platitudes.
- **🎯  Focus Mode** — Pomodoro-style work sessions. Pip keeps time, stays quiet.
- **🌬️  Breathe Mode** — Guided 4-7-8, box breathing, and simple deep breathing.
- **🧘  Meditate Mode** — Body scan, loving-kindness, and just-sitting meditations.
- **🎨  Custom UI** — Dark, cozy theme with real-time ASCII art expressions.
- **🔌  100% Local** — No cloud APIs, no data collection, fully offline.

## 🚀  Quick Start

```bash
# Clone and install
git clone <this-repo>
cd focusfriend
pip install -r requirements.txt

# Download Gemma 4 12B GGUF model
huggingface-cli download unsloth/gemma-4-12b-it-GGUF \
  --include "gemma-4-12b-it-Q4_K_M.gguf" \
  --local-dir ./models

# Launch
python app.py
```

## 🧠  Model

| Model | Size | Purpose | License |
|-------|------|---------|---------|
| Gemma 4 12B | 12B | Conversational AI + wellness guidance | Apache 2.0 (Gemma) |

Runs on a laptop with Q4_K_M quantization (~7.7 GB).

## 🏅  Hackathon Track

**Thousand Token Wood** — A delightful AI experience that wouldn't exist without AI.

### Bonus Badges
- 🦙  **Tiny Titan** — Runs on ≤4B param model option available
- 🎨  **Off-Brand** — Fully custom dark theme CSS + JavaScript
- 🔌  **Off the Grid** — Fully local, no API calls
- 📓  **Field Notes** — Blog post about AI wellness companions

## 🎭  Meet Pip

```
     _____
    /     \
   | •   • |   ✨  Hey! I'm Pip.
   |   ▿   |   Your focus buddy.
   \  ~~~  /
    | | | |
    |_| |_|
```

Pip has 20+ expressions that change based on the conversation context — from
determined (focus mode) to peaceful (meditation) to gently concerned (checking
on your wellbeing).

## 🤝  Credits

Built with ❤️ for the Build Small Hackathon 2026.
The character, personality, and experience are AI-generated — making the AI
**load-bearing for the experience itself.**
