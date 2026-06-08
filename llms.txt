# Build Small Hackathon — PRD
# Project Requirements Document

> Three Gradio apps targeting all tracks + maximum badges + sponsor prizes.
> Hack window: June 5-15, 2026. Deadline: June 15.

> This file is the master PRD and stays English-only. Per-project UIs and
> READMEs may use additional stylistic content for their own artifacts; this
> doc does not enumerate those choices.

---

## Overview

- **Name:** Build Small Hackathon 2026 — Team nbiish
- **Version:** 0.4.0 — Cedar-Copper Edition
- **Description:** Multi-project hackathon entry targeting $48K+ prize pool across Backyard AI and Thousand Token Wood tracks. Three Gradio apps using small models (≤32B) with maximum bonus badge coverage.
- **Aesthetic:** Cedar-copper visual language — sky-to-sunrise palette (water-blue → cedar → copper → sun-amber → birch-cream), biophilic motifs, sky-to-water gradient banners. Shared CSS variables live in `shared/cedar_copper_tokens.py`.
- **Purpose:** Win prizes across tracks, badges, and sponsor categories by building delightful, useful AI apps that run locally.
- **UX:** Gradio web apps (gr.Blocks + mount_gradio_app custom frontends), hosted on HF Spaces.

---

## Rules

### Naming & Comments

- Descriptive project names: CritterCalm, FocusFriend, TinyBard
- Docstrings on all public functions. Comments on non-obvious logic.

### Always

- Models ≤ 32B total params per project
- Gradio app hosted as HF Space
- Local-first (no cloud APIs = Off the Grid badge)
- GGUF quantized models for local inference
- Python 3.10+ with pinned requirements
- Cedar-copper aesthetic consistency across all UIs (palette tokens in `shared/cedar_copper_tokens.py`)

### Never

- Cloud API calls in production path
- Hardcoded secrets or API keys
- Models > 32B params
- Default Gradio look without customization attempt

### If

- If custom frontend is feasible → use `mount_gradio_app` for Off-Brand badge
- If model ≤ 4B → tag Tiny Titan eligible
- If using llama.cpp runtime → tag Llama Champion
- If fine-tuning is done → publish model to HF Hub

---

## Infrastructure

### Gradio 6.0 + MCP Server

- `gradio.Server` is **NOT** in Gradio 6.0 stable. Use `mount_gradio_app(fastapi_app, blocks, path="/gradio")` instead.
- MCP server mode: `demo.launch(mcp_server=True)` or `GRADIO_MCP_SERVER=true` env var.
- Custom frontends: Serve static HTML/CSS/JS via FastAPI, mount Gradio at `/gradio` for API + MCP.
- `@gradio/client` CDN: `https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js` (ES module, use `type="module"`).
- Theme parameters: `css`, `head`, `theme` moved from `gr.Blocks(...)` to `app.launch(...)` in Gradio 6.0.
- Chatbot API: Gradio 6.0 requires `{"role": "user|assistant", "content": "..."}` dicts (not tuples).

### HF Agents CLI

- `hf` CLI is installed (v1.18.0). See `skill://hf-cli` for full command reference.
- Install expert skills: `hf skills add --global` or `hf skills add --claude --global`.
- Spaces managed via: `hf repos create <name> --type space --space-sdk gradio --public`.
- Deploy: `git remote add hf https://huggingface.co/spaces/<user>/<space>` then `git push hf main`.
- HF README metadata: `colorTo` must be one of `[red, yellow, green, blue, indigo, purple, pink, gray]` (no `emerald`/`amber`).
- HF README metadata: `emoji` must match `/\p{Extended_Pictographic}/u` — only the standard emoji block is allowed; decorative Unicode glyphs (solar/astrological/typographic symbols) fail validation. Use a real emoji.

### Local Test Environment

- Python: miniconda3 (Python 3.12)
- Gradio: 6.0.0
- llama-cpp-python: installed via conda-forge (v0.3.16)
- Available GGUF models:
  - VibeThinker-1.5B.Q8_0.gguf (in HF cache)
  - LFM2-1.2B-Q4_K_M.gguf (in HF cache)
  - LFM2-8B-A1B-Q4_K_M.gguf (in ggufy/models/)
- Missing GGUF models (need download): Gemma 4 12B, Dolphin-X1-8B

### Local Servers

All 3 apps run simultaneously on different ports for visual inspection:

| Project | URL | Stack | HF Space |
|---|---|---|---|
| TinyBard | http://localhost:7861/ | FastAPI + Gradio Blocks | nbiish/tinybard |
| FocusFriend | http://localhost:7862/ | Gradio 6.0 | nbiish/focusfriend |
| CritterCalm | http://localhost:7863/ | Gradio 6.0 | nbiish/crittercalm |

---

## Projects

### 1. CritterCalm (Backyard AI)

- **Status:** Code complete. Deployed. Locally tested. Cedar-copper UI applied.
- **Stack:** OmniVoice (0.6B) + Dolphin-X1-8B (8B) + Kokoro TTS (82M) = 8.7B params
- **Badges:** Off the Grid, Well-Tuned (TBD), Field Notes, Llama Champion (TBD), Off-Brand (custom banner)
- **GitHub:** github.com/nbiish/crittercalm
- **HF Space:** huggingface.co/spaces/nbiish/crittercalm
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/crittercalm-repo

### 2. FocusFriend (Thousand Token Wood)

- **Status:** Code complete. Deployed. Locally tested. Cedar-copper UI applied. Gradio 6 Chatbot dict-format fixed.
- **Stack:** Gemma 4 12B (12B) via llama-cpp-python
- **Badges:** Off-Brand (sun-amber custom theme), Off the Grid, Field Notes
- **GitHub:** github.com/nbiish/focusfriend
- **HF Space:** huggingface.co/spaces/nbiish/focusfriend
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/focusfriend-repo
- **Note:** Gemma 4 12B GGUF not yet downloaded. Need `huggingface-cli download unsloth/gemma-4-12b-it-GGUF --include "gemma-4-12b-it-Q4_K_M.gguf" --local-dir ./models`

### 3. TinyBard (Thousand Token Wood + Tiny Titan + Llama Champion)

- **Status:** Code complete. Deployed. Locally tested end-to-end (game loop). Cedar-copper CRT UI applied.
- **Concept:** ≤4B LLM generates 5-min interactive text adventures in a CRT terminal aesthetic.
- **Stack:** VibeThinker 1.5B (1.5B) via llama-cpp-python + procedural fallback engine
- **Architecture:** FastAPI + mount_gradio_app at /gradio. Custom HTML/CSS/JS frontend. MCP tools: start_game, make_choice.
- **Badges:** Llama Champion, Tiny Titan (1.5B < 4B), Off-Brand (custom CRT), Off the Grid, Field Notes
- **Prize targets:** Tiny Titan ($1K), Thousand Token Wood track, Bonus Quest Champion potential
- **GitHub:** github.com/nbiish/tinybard
- **HF Space:** huggingface.co/spaces/nbiish/tinybard
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/tinybard

---

## TODO

> Keep tasks atomic and testable.

### In Progress

- [ ] Test CritterCalm voice cloning pipeline end-to-end
- [ ] Test FocusFriend all 4 modes (Chat, Focus, Breathe, Meditate) with real model
- [ ] Record demo videos (2-3 min each)
- [ ] Post to social media
- [ ] Write Field Notes blog posts (3 — one per project)
- [ ] Share agent traces to HF Hub (Sharing is Caring badge)

### Completed

- [x] CritterCalm v1 code complete (11 files) — Cedar-copper UI
- [x] FocusFriend v1 code complete (16 files) — Cedar-copper UI + Gradio 6 dict Chatbot
- [x] TinyBard v1 code complete (8 files) — LLM + procedural fallback, CRT UI, clean FastAPI JSON
- [x] GitHub repos created (nbiish/crittercalm, nbiish/focusfriend, nbiish/tinybard)
- [x] HF Spaces created and deployed (all 3)
- [x] Monorepo structure with projects/ directory + shared/ aesthetic module
- [x] INTELLIGENCE.md — full hackathon landscape analysis
- [x] SUBMISSION_DRAFTS.md — social posts + Field Notes drafts
- [x] HF CLI installed + skills configured (`hf skills add --global`)
- [x] llama-cpp-python installed (conda-forge v0.3.16)
- [x] Local verification: all 3 apps run on ports 7861/7862/7863
- [x] TinyBard end-to-end game loop verified (start → choose → next scene)
- [x] FocusFriend chat verified (user message → Pip reply)
- [x] CritterCalm UI navigation verified (all 3 tabs render)

---

## Short-term Goals

- Test all 3 apps locally with real GGUF models (currently running with procedural fallbacks)
- Record demo videos and post to social media
- Write and publish Field Notes blog posts
- Share agent traces for Sharing is Caring badge
- Polish UIs for demo appeal

---

## Reference

- CritterCalm: projects/crittercalm/ + github.com/nbiish/crittercalm
- FocusFriend: projects/focusfriend/ + github.com/nbiish/focusfriend
- TinyBard: projects/tinybard/ + github.com/nbiish/tinybard
- Aesthetic module: shared/cedar_copper_tokens.py
- ML Intern: github.com/huggingface/ml-intern
- HF Agents CLI: huggingface.co/docs/hub/en/agents-cli
- Gradio MCP: gradio.app/guides/model-context-protocol