---
title: ᐴ CritterCalm ᔔ
emoji: 🐾
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 6.0.0
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
  - anishinaabe
  - solarpunk
---

# ◈──◆──◇ ᐴ CRITTERCALM ᔔ MAANAMEWIN / VOICE-COMFORT FOR THE FOUR-LEGGEDS ◇──◆──◈

> **Maanamewin** — in Anishinaabemowin, the act of giving comfort through voice.
> Clone your voice. Calm your companion. Even across distance.

CritterCalm clones your voice using state-of-the-art open-source AI, then generates
personalized calming audio sessions for your pets. Dogs, cats, chickens, birds,
rabbits, horses — every animal responds to their person's voice.

## ☼ GASHKITOONAN / CAPABILITIES ◈

- **🎤  Voice Cloning** — Clone your voice from just 3-10 seconds of audio (OmniVoice 0.6B)
- **🐕  Multi-Animal Support** — Species-specific calming techniques for 6 animal types
- **🎯  Situation-Aware** — Tailored scripts for anxiety, storms, vet visits, and more
- **❀  Anishinaabe-Solarpunk UI** — Cedar-and-sun palette, sky-to-water gradient banner
- **☼  Custom ASP Theme** — Serif headers, sun-amber CTAs, moss-green accents
- **🔌  100% Local** — No cloud APIs, no data collection, fully offline
- **📚  Science-Backed** — Based on animal cognition and psychoacoustics research

## ☼ NITAM-AABAJICHIGANAN / PREREQUISITES ◈

- Python 3.10+
- ~9GB disk for models (OmniVoice, Dolphin-X1, Kokoro)
- ~10GB RAM (CPU) or Metal/CUDA for GPU

## ☼ AABAJITOOWINAN / INSTALLATION ◈

```bash
git clone https://github.com/nbiish/crittercalm.git
cd crittercalm
pip install -r requirements.txt

# Models auto-download on first run from Hugging Face Hub
python app.py
```

Then open <http://localhost:7863/>.

## ☼ ZHOONIYAAWICHIGEWIN / MODEL STACK ◈

| Model | Size | Purpose | License |
|-------|------|---------|---------|
| OmniVoice | 0.6B | Voice cloning + TTS | Apache 2.0 |
| Dolphin-X1-8B | 8B | Calming script generation | Llama 3.1 |
| Kokoro TTS | 82M | Built-in soothing voices (fallback) | Apache 2.0 |

**Total: ~8.7B params** (well under the 32B limit)

## ☼ MCP KINOOMAAGEWINAN / MCP TOOLS ◈

Runs with `mcp_server=True` — Streamable HTTP MCP server at `/gradio/gradio_api/mcp/`:

- `clone_voice(audio_path, transcript, ref_text)` — Clone a voice from a 10s sample
- `generate_calming_session(animal, situation, duration, voice_profile)` — Generate audio
- `play_calming(audio_id)` — Play the generated session

## ☼ GIIZHIITAA / BADGES ◈

- 🔌  **Off the Grid** — Fully local, no API calls
- 🎯  **Well-Tuned** — Fine-tuned voice embeddings for pet-directed speech
- 📓  **Field Notes** — Blog post on animal psychoacoustics + voice cloning
- 🎨  **Off-Brand** — Anishinaabe-Solarpunk theme with sky-to-sunrise palette

## ☼ INA-WAABANDA'IWEWIN / PROJECT STRUCTURE ◈

```
crittercalm/
├── app.py                       # Main Gradio application
├── voice_cloning/               # OmniVoice integration
│   └── openvoice_cloner.py
├── content/                     # Script generation + templates
│   ├── script_generator.py
│   └── templates.py
├── utils/                       # Audio processing utilities
│   └── audio_utils.py
├── requirements.txt
└── README.md
```

## ☼ GANAWENDAAGWAD / SECURITY ◈

Voice recordings, cloned profiles, and generated audio **never leave the device**.
PQC for any future API key material via the `pqc-secrets` skill (ML-KEM-768 + AES-256-GCM).

---

◈──◆──◇ ☼ CritterCalm v1.0 · Cedar Edition · Anishinaabe Solarpunk ◇──◆──◈

Built with ☼ for the Build Small Hackathon 2026.
