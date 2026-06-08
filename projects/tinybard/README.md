---
title: TinyBard
emoji: ⚔
colorFrom: green
colorTo: blue
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
---

# ⚔ TinyBard — Micro Interactive Text Adventure Generator

**A ≤4B LLM generates 5-minute interactive text adventures with a retro CRT terminal UI.**

TinyBard uses gr.Server (FastAPI) with a fully custom HTML/CSS/JS frontend and MCP server mode enabled.
Every adventure is procedurally generated — rooms, NPCs, items, and branching narratives on the fly.

## Features

- **Dynamic Adventures** — LLM generates unique story beats for every playthrough
- **3 Genres** — Fantasy, Sci-Fi, Cyberpunk
- **CRT Terminal UI** — Retro pixel-art aesthetic with scanlines and phosphor glow
- **MCP Server** — Exposes `start_game` and `make_choice` as MCP tools for AI agent integration
- **100% Local** — No cloud APIs. Runs on llama.cpp with GGUF quantized models
- **Procedural Fallback** — Full game engine works even without the LLM model loaded

## Quick Start

```bash
git clone <this-repo>
cd tinybard
pip install -r requirements.txt

# Download model (Q4_K_M quant, ~1GB)
huggingface-cli download mradermacher/VibeThinker-1.5B-GGUF \
  --include "VibeThinker-1.5B.Q8_0.gguf" \
  --local-dir ./models

# Set model path
export TINYBARD_MODEL_PATH=./models/VibeThinker-1.5B.Q8_0.gguf

# Launch
python app.py
```

## Model

| Model | Size | Purpose | License |
|-------|------|---------|---------|
| VibeThinker 1.5B | 1.5B | Interactive story generation | Apache 2.0 |

Fits the Tiny Titan badge (≤4B params). Runs on any laptop.

## MCP Integration

TinyBard runs with `mcp_server=True`, exposing these tools:

- **`start_game`** — Start a new adventure. Args: `genre` (fantasy/scifi/cyberpunk)
- **`make_choice`** — Submit a player choice. Args: `choice`, `genre`, `step`, `health`, `history_json`

Connect from any MCP client (Claude Desktop, Cursor, etc.) to the SSE endpoint.

## Hackathon Track

**Thousand Token Wood** + **Tiny Titan** + **Llama Champion**

### Bonus Badges
- **Llama Champion** — Uses llama.cpp runtime
- **Tiny Titan** — Model is 1.5B (well under 4B limit)
- **Off-Brand** — Fully custom gr.Server frontend (not gr.Blocks)
- **Off the Grid** — Fully local, no API calls
- **Field Notes** — Blog post about tiny model interactive fiction

## Credits

Built for the Build Small Hackathon 2026.
The AI is load-bearing: every story, choice, and narrative arc is generated live.
