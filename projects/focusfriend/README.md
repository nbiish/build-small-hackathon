---
title: ᐴ FocusFriend ᔔ
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
  - inference-api
  - cooldowns
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
- A Hugging Face token (anonymous works for many small models)
- ~100MB disk, ~256MB RAM — inference is serverless

## ☼ AABAJITOOWINAN / INSTALLATION ◈

```bash
git clone https://github.com/nbiish/focusfriend.git
cd focusfriend
pip install -r requirements.txt

# Optional: pick a model (default: Qwen/Qwen2.5-7B-Instruct)
export INFERENCE_MODEL="Qwen/Qwen2.5-7B-Instruct"

# Optional: set the HF token
export HF_TOKEN="hf_..."

# Optional: tune the cooldown
export FOCUSFRIEND_COOLDOWN_SECONDS=10

python app.py
```

Then open <http://localhost:7862/>.

## ☼ ZHOONIYAAWICHIGEWIN / MODEL ◈

| Model (default) | Size | Purpose | License |
|---|---|---|---|
| Qwen2.5-7B-Instruct | 7B | Wellness companion chat | Apache 2.0 |
| Meta-Llama-3-8B-Instruct | 8B | Alternative | Llama 3 Community |
| gemma-2-9b-it | 9B | Alternative | Gemma License |

## ☼ MCP KINOOMAAGEWINAN / MCP TOOLS ◈

Runs with `mcp_server=True` — Streamable HTTP MCP server at `/gradio/gradio_api/mcp/`:

- `chat_handler(message, history, mode)` — Stream Pip's response to a message
- `set_mode(mode)` — Switch Pip's active mode (chat, focus, breathe, meditate)
- `on_focus_start(duration)` — Begin a focus session timer
- `start_breathe_session(technique)` — Begin breathing exercise
- `start_meditate_session(duration, style)` — Begin meditation

## ☼ GIIZHIITAA / BADGES ◈

- 🎨  **Off-Brand** — Anishinaabe-Solarpunk CSS theme with sun-amber gradients
- 📓  **Field Notes** — Blog post about AI wellness companions
- 🦙  **Tiny Titan** — Default model is 7B; can switch to 1.5B Qwen for true Tiny Titan
- 🌀  **Cooldowns** — Serverless inference with built-in credit protection
- ☁  **HF Inference API** — Uses Hugging Face serverless backend (no local GGUF build)

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
