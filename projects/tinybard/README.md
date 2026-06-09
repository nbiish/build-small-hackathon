---
title: ᐴ TinyBard ᔔ
emoji: ☀️
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
  - thousand-token-wood
  - build-small-hackathon
  - tiny-titan
  - off-brand
  - mcp-server
  - anishinaabe
  - solarpunk
  - inference-api
  - cooldowns
---

# ◈──◆──◇ ᐴ TINYBARD ᔔ AADIZOOKAAN-AKINOOMAAGEWIN / STORY-TELLING ENGINE ◇──◆──◈

> **A small LLM fires five-minute interactive text adventures in a cedar-and-copper CRT terminal.**
>
> ᐴ The land remembers the stories. ᔔ  ☼ ☘ ≈

TinyBard uses FastAPI + `mount_gradio_app` (Gradio 6.0) with a fully custom HTML/CSS/JS frontend, **MCP server mode** enabled, and an **HF Inference API** backend. Every adventure is procedurally generated — rooms, NPCs, items, and branching narratives on the fly.

## ◆ GASHKITOONAN / CAPABILITIES ◈

- **◇ Dynamic Adventures ◇** — LLM generates unique story beats for every playthrough
- **◇ Three Aadizookaanan / Genres ◇** — Aadizookaan (Fantasy), Ish piming (Sci-Fi), Mashkodewaazibi (Cyberpunk)
- **◇ Misko-Aki / CRT Terminal ◇** — Cedar-copper cabinet, sun-amber phosphor, frost-on-glass scanlines
- **◇ MCP Kinoomaagewinan / Tools ◇** — `start_game` and `make_choice` exposed as MCP tools
- **◇ Giiwenaabik / Inference API ◇** — Serverless HF Inference API; no local GGUF, no build step
- **◇ Asabiikesiwin / Cooldown ◇** — 6s default between inference calls to protect your credit budget
- **◇ Bmaad-ziibi / Procedural Fallback ◇** — Full engine works without the LLM
- **◇ Anishinaabe-Solarpunk ◇** — Sky-to-sunrise palette, syllabic framings, biophilic motifs

## ☼ NITAM-AABAJICHIGANAN / PREREQUISITES ◈

- Python 3.10+
- A Hugging Face token (for the Inference API; many small models work anonymously)
- ~100MB disk, ~256MB RAM — the model is serverless, not local

## ◇ AABAJITOOWINAN / INSTALLATION ◈

```bash
git clone https://github.com/nbiish/tinybard.git
cd tinybard
pip install -r requirements.txt

# Optional: pick a model (default: Qwen/Qwen2.5-1.5B-Instruct — small + fast + free)
export INFERENCE_MODEL="Qwen/Qwen2.5-1.5B-Instruct"
# Or for the originally-intended VibeThinker 1.5B:
# export INFERENCE_MODEL="mradermacher/VibeThinker-1.5B-GGUF"

# Optional: set the HF token (anonymous works for many models)
export HF_TOKEN="hf_..."

# Optional: tune the cooldown
export TINYBARD_COOLDOWN_SECONDS=6

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
curl -X POST http://localhost:7860/api/game/start \
  -H "Content-Type: application/json" \
  -d '{"genre": "fantasy"}'
```

Returns clean JSON: `{"story", "choices", "health", "step", "game_over", "history"}`.

```bash
curl http://localhost:7860/api/model_status
```

Returns: `{"model": "...", "cooldown": {"active": bool, "remaining_seconds": float, "window_seconds": float}}`.

## ◈ MODEL ◇

| Model (default) | Size | Purpose | License |
|---|---|---|---|
| Qwen2.5-1.5B-Instruct | 1.5B | Interactive story generation | Apache 2.0 |
| VibeThinker 1.5B | 1.5B | Alternative — also tiny | Apache 2.0 |

Override `INFERENCE_MODEL` to any model that supports `chat_completion` on the HF Inference API. The 1.5B defaults fit the **Tiny Titan** badge.

## ◇ MCP KINOOMAAGEWINAN / TOOLS ◈

TinyBard runs with `mcp_server=True`, exposing these tools (also available as FastAPI endpoints):

- **`/api/game/start`** (POST `{"genre": "fantasy|scifi|cyberpunk"}`) — Start an adventure
- **`/api/game/choice`** (POST `{choice, genre, step, health, history}`) — Submit a player choice
- **`/api/model_status`** (GET) — Check the inference model + cooldown state

Connect from any MCP client (Claude Desktop, Cursor, etc.) to the SSE endpoint at `/gradio/gradio_api/mcp/`.

## ◇ GIIZHIITAA / BADGE TARGETS ◇

- **◆ Tiny Titan** — Model ≤ 1.5B (well under 4B limit)
- **◆ Off-Brand** — Fully custom FastAPI+Gradio frontend
- **◆ Field Notes** — Blog post about tiny model interactive fiction

## ☼ GANAWENDAAGWAD / SECURITY ◈

PQC standard for any future API keys via the `pqc-secrets` skill (ML-KEM-768 + AES-256-GCM). At present, only the HF token is in flight (read from env var, never written to disk).

## ◇ AABAAJICHIGANAN / COOLDOWNS ◈

The `shared/inference_client.py` module enforces per-project cooldowns. Cooldown protects your HF/Modal credit budget from runaway re-rolls. Defaults:

- `tinybard`: 6s
- `focusfriend`: 10s
- `crittercalm`: 12s

Override per project via Space env vars (`TINYBARD_COOLDOWN_SECONDS`, etc.).

---

◈──◆──◇ ☼ TinyBard v1.1 · Cedar Edition · Anishinaabe Solarpunk · Inference API ◇──◆──◈
