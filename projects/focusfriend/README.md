---
title: ᐴ FocusFriend ᔔ
emoji: ☼
colorFrom: indigo
colorTo: yellow
sdk: gradio
sdk_version: 6.0.0
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
  - anishinaabe
  - solarpunk
---

# ◈──◆──◇ ᐴ FOCUSFRIEND ᔔ PIP, YOUR CEDAR-AND-SUN COMPANION ON THE LAKE ◇──◆──◈

> **Aaniin, amiikwens** — I am Pip, the friend of the moss and the small winds.
> Sit. Breathe. The sun is in no hurry.

Pip is a wise, dry-witted, slightly mischievous but genuinely caring wellness
companion. Not a sycophantic cheerleader. Think: "your friend who's been through
therapy and wants you to actually feel better, not just hear platitudes."

## ☼ GASHKITOONAN / CAPABILITIES ◈

- **💬  Chat Mode** — Talk to Pip. Real conversation, no corny platitudes.
- **🎯  Focus Mode** — Pomodoro-style work sessions. Pip keeps time, stays quiet.
- **🌬️  Breathe Mode** — Guided 4-7-8, box breathing, and simple deep breathing.
- **🧘  Meditate Mode** — Body scan, loving-kindness, and just-sitting meditations.
- **☼  Anishinaabe-Solarpunk UI** — Sky-to-sunrise palette, sun-amber gradients, biophilic motifs.
- **☘  Custom CSS Theme** — Cedar-copper shrine for Pip, water-blue surfaces, birch-cream text.
- **🔌  100% Local** — No cloud APIs, no data collection, fully offline.

## ☼ NITAM-AABAJICHIGANAN / PREREQUISITES ◈

- Python 3.10+
- ~7.7GB disk for GGUF model
- ~12GB RAM (CPU inference) or Metal/CUDA for GPU

## ☼ AABAJITOOWINAN / INSTALLATION ◈

```bash
git clone https://github.com/nbiish/focusfriend.git
cd focusfriend
pip install -r requirements.txt

# Download Gemma 4 12B GGUF model
huggingface-cli download unsloth/gemma-4-12b-it-GGUF \
  --include "gemma-4-12b-it-Q4_K_M.gguf" \
  --local-dir ./models

python app.py
```

Then open <http://localhost:7862/>.

## ☼ ZHOONIYAAWICHIGEWIN / MODEL ◈

| Model | Size | Purpose | License |
|-------|------|---------|---------|
| Gemma 4 12B (Q4_K_M) | 12B params, ~7.7GB | Conversational AI + wellness guidance | Apache 2.0 (Gemma) |

## ☼ MCP KINOOMAAGEWINAN / MCP TOOLS ◈

Runs with `mcp_server=True` — Streamable HTTP MCP server at `/gradio/gradio_api/mcp/`:

- `chat_handler(message, history, mode)` — Stream Pip's response to a message
- `set_mode(mode)` — Switch Pip's active mode (chat, focus, breathe, meditate)
- `on_focus_start(duration)` — Begin a focus session timer
- `start_breathe_session(technique)` — Begin breathing exercise
- `start_meditate_session(duration, style)` — Begin meditation

## ☼ GIIZHIITAA / BADGES ◈

- 🎨  **Off-Brand** — Anishinaabe-Solarpunk CSS theme with sun-amber gradients
- 🔌  **Off the Grid** — Fully local, no API calls
- 📓  **Field Notes** — Blog post about AI wellness companions
- 🦙  **Tiny Titan** — Model option ≤4B available

## ☼ GANAWAABANDAAN / MEET PIP ◈

```
    _____
   /     \
  | •   • |   ☼  Hey! I'm Pip.
  |   ▿   |   Your focus buddy.
  \  ~~~  /
   | | | |
   |_| |_|
```

Pip has 20+ expressions that change based on the conversation context — from
determined (focus mode) to peaceful (meditation) to gently concerned (checking
on your wellbeing).

## ☼ GANAWENDAAGWAD / SECURITY ◈

Standard gradio local-app practices. PQC for any future API key material via
the `pqc-secrets` skill (ML-KEM-768 + AES-256-GCM).

---

◈──◆──◇ ☼ FocusFriend v1.0 · Cedar Edition · Anishinaabe Solarpunk ◇──◆──◈

Built with ☼ for the Build Small Hackathon 2026.
The character, personality, and experience are AI-generated — making the AI
**load-bearing for the experience itself.**
