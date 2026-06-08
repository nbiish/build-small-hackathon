---
title: ᐴ TinyBard ᔔ
emoji: ☼
colorFrom: blue
colorTo: yellow
sdk: gradio
sdk_version: 6.0.0
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - text-adventure
  - interactive-fiction
  - llama-cpp
  - thousand-token-wood
  - build-small-hackathon
  - tiny-titan
  - llama-champion
  - off-brand
  - off-the-grid
  - mcp-server
  - anishinaabe
  - solarpunk
---

# ◈──◆──◇ ᐴ TINYBARD ᔔ AADIZOOKAAN-AKINOOMAAGEWIN / STORY-TELLING ENGINE ◇──◆──◈

> **A ≤4B LLM fires five-minute interactive text adventures in a cedar-and-copper CRT terminal.**
>
> ᐴ The land remembers the stories. ᔔ  ☼ ☘ ≈

TinyBard uses FastAPI + `mount_gradio_app` (Gradio 6.0) with a fully custom HTML/CSS/JS frontend and **MCP server mode** enabled. Every adventure is procedurally generated — rooms, NPCs, items, and branching narratives on the fly.

## ◆ GASHKITOONAN / CAPABILITIES ◈

- **◇ Dynamic Adventures ◇** — LLM generates unique story beats for every playthrough
- **◇ Three Aadizookaanan / Genres ◇** — Aadizookaan (Fantasy), Ish piming (Sci-Fi), Mashkodewaazibi (Cyberpunk)
- **◇ Misko-Aki / CRT Terminal ◇** — Cedar-copper cabinet, sun-amber phosphor, frost-on-glass scanlines
- **◇ MCP Kinoomaagewinan / Tools ◇** — `start_game` and `make_choice` exposed as MCP tools
- **◇ Zhooniyaa / 100% Local ◇** — No cloud APIs. Runs on llama.cpp with GGUF quantized models
- **◇ Bmaad-ziibi / Procedural Fallback ◇** — Full engine works without the LLM model loaded
- **◇ Anishinaabe-Solarpunk ◇** — Sky-to-sunrise palette, Anishinaabe syllabic framings, biophilic motifs

## ☼ NITAM-AABAJICHIGANAN / PREREQUISITES ◈

- Python 3.10+
- ~1GB disk for GGUF model
- ~2GB RAM (CPU inference) or Metal/CUDA for GPU

## ◇ AABAJITOOWINAN / INSTALLATION ◈

```bash
git clone https://github.com/nbiish/tinybard.git
cd tinybard
pip install -r requirements.txt

# Download model (Q8_0 quant, ~1.6GB)
huggingface-cli download mradermacher/VibeThinker-1.5B-GGUF \
  --include "VibeThinker-1.5B.Q8_0.gguf" \
  --local-dir ./models

export TINYBARD_MODEL_PATH=./models/VibeThinker-1.5B.Q8_0.gguf

python app.py
```

Then open <http://localhost:7860/>.

## ◈ WAABANDA'IWEWIN / EXAMPLES ◇

```text
╭─────────────────────────────────────╮
│  ᐴ AADIZOOKAAN / FANTASY ᔔ          │
╰─────────────────────────────────────╯

You stand before the gates of the Whisperwood. The ancient trees
hum with a faint violet energy...

[ Take the golden key ]   [ Drink the mossy vial ]   [ Press forward ]
```

## ☼ NAANAAGADAWENINDIZOWIN / VERIFICATION ◈

```bash
curl -X POST http://localhost:7860/gradio/gradio_api/call/start_game \
  -H "Content-Type: application/json" \
  -d '{"data":["fantasy"]}'
```

Returns SSE event stream with `story`, `choices`, `health`, `step`, `game_over`, `history_json`.

## ◈ MODEL ◇

| Model | Size | Purpose | License |
|-------|------|---------|---------|
| VibeThinker 1.5B (Q8_0) | 1.5B params, ~1.6GB | Interactive story generation | Apache 2.0 |

Fits the **Tiny Titan** badge (≤4B params). Runs on any laptop.

## ◇ MCP KINOOMAAGEWINAN / TOOLS ◈

TinyBard runs with `mcp_server=True`, exposing these tools:

- **`start_game(genre: str)`** — Start a new adventure. Genre: `fantasy` / `scifi` / `cyberpunk`
- **`make_choice(choice, genre, step, health, history_json)`** — Submit a player choice to advance the story

Connect from any MCP client (Claude Desktop, Cursor, etc.) to the SSE endpoint at `/gradio/gradio_api/mcp/`.

## ◈ GIIZHIITAA / BADGE TARGETS ◇

- **◆ Llama Champion** — Uses llama.cpp runtime
- **◆ Tiny Titan** — Model is 1.5B (well under 4B limit)
- **◆ Off-Brand** — Fully custom FastAPI+Gradio frontend
- **◆ Off the Grid** — Fully local, no API calls
- **◆ Field Notes** — Blog post about tiny model interactive fiction

## ☼ GANAWENDAAGWAD / SECURITY ◈

PQC standard for any future API keys via the `pqc-secrets` skill (ML-KEM-768 + AES-256-GCM). At present, the model is loaded from local GGUF — no key material in flight.

---

◈──◆──◇ ☼ TinyBard v1.0 · Cedar Edition · Anishinaabe Solarpunk ◇──◆──◈
