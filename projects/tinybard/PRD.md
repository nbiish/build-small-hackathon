# DOX framework

- DOX is a highly performant `llms.txt` hierarchy installed here
- Agent must follow DOX instructions across any edits

## Purpose

- **Name:** Build Small Hackathon 2026 — Team nbiish
- **Version:** 0.5.0 — Cedar-Copper Edition (HF Inference API)
- **Aesthetic:** Cedar-copper visual language — sky-to-sunrise palette (water-blue → cedar → copper → sun-amber → birch-cream), biophilic motifs, sky-to-water gradient banners. Shared CSS variables live in `shared/cedar_copper_tokens.py`.
- **Purpose:** Win prizes across tracks, badges, and sponsor categories by building delightful, useful AI apps that run locally.
- **UX:** Gradio web apps (gr.Blocks + mount_gradio_app custom frontends), hosted on HF Spaces.
- **Hack window:** June 5-15, 2026. Deadline: June 15.

> This file is the master PRD and stays English-only. Per-project UIs and READMEs may use additional stylistic content for their own artifacts.

## Core Contract

- `llms.txt` files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable `llms.txt` plus every parent `llms.txt` above it

## Read Before Editing

1. Read the root `llms.txt`
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every `llms.txt` found along each route
5. If a parent `llms.txt` lists a child `llms.txt` whose scope contains the path, read that child and continue from there
6. Use the nearest `llms.txt` as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Local Contracts

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

### Inference Architecture (v0.5+)

- **All LLM inference** is now via the **Hugging Face Inference API** (serverless). No more local GGUF, no `llama-cpp-python` compile step.
- Shared module: `shared/inference_client.py` provides `cooldown_status()`, `cooldown_active()`, `generate()`, and `chat_messages()`.
- Default model: `Qwen/Qwen2.5-1.5B-Instruct` (free tier, fast, well-suited to chat). Override via `INFERENCE_MODEL`.
- Per-project model override: `TINYBARD_MODEL`, `FOCUSFRIEND_MODEL`, `CRITTERCALM_MODEL`.
- **Cooldowns** enforce a per-project minimum gap between inference calls (protects HF/Modal credit budget):
  - `tinybard`: 6s
  - `focusfriend`: 10s
  - `crittercalm`: 12s
  - Override via `TINYBARD_COOLDOWN_SECONDS`, etc., or global `INFERENCE_COOLDOWN_SECONDS`.
- **Always-fallback:** every LLM call falls back to procedural / template output if inference fails or is in cooldown. No LLM call ever blocks the UX.
- HF Spaces are the dev/test environment — iterate live at `huggingface.co/spaces/nbiish/{tinybard,focusfriend,crittercalm}` rather than localhost.

### Local Test Environment

- Python: miniconda3 (Python 3.12)
- Gradio: 6.0.0
- `huggingface_hub` (for Inference API client)
- Inference is serverless — no local model files needed unless you opt in to local mode

### Local Servers (optional)

Local servers were used during v0.4 development for visual inspection. v0.5+ prefers iterating on the live HF Spaces (which use your HF/Modal compute credits). Local servers can still be run for dev:

| Project | URL | Stack | HF Space |
|---|---|---|---|
| TinyBard | http://localhost:7861/ | FastAPI + Gradio Blocks | nbiish/tinybard |
| FocusFriend | http://localhost:7862/ | Gradio 6.0 | nbiish/focusfriend |
| CritterCalm | http://localhost:7863/ | Gradio 6.0 | nbiish/crittercalm |

## Projects

### 1. CritterCalm (Backyard AI)

- **Status:** Code complete. Deployed. HF Inference API + cooldowns wired for script generation. OmniVoice voice cloning still requires local install.
- **Stack:** OmniVoice (0.6B, local optional) + Kokoro TTS (82M, local optional) + Qwen2.5-7B (default) via HF Inference API
- **Badges:** Off the Grid, Well-Tuned (TBD), Field Notes, Off-Brand
- **GitHub:** github.com/nbiish/crittercalm
- **HF Space:** huggingface.co/spaces/nbiish/crittercalm
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/crittercalm-repo

### 2. FocusFriend (Thousand Token Wood)

- **Status:** Code complete. Deployed. HF Inference API + cooldowns wired. Gradio 6 Chatbot dict-format fixed.
- **Stack:** Qwen2.5-7B (default) via HF Inference API
- **Badges:** Off-Brand (sun-amber custom theme), Field Notes, Cooldowns badge
- **GitHub:** github.com/nbiish/focusfriend
- **HF Space:** huggingface.co/spaces/nbiish/focusfriend
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/focusfriend-repo

### 3. TinyBard (Thousand Token Wood + Tiny Titan + Llama Champion)

- **Status:** Code complete. Deployed. HF Inference API + cooldowns wired. Local test verified (procedural fallback + cooldown UI).
- **Concept:** ≤4B LLM generates 5-min interactive text adventures in a CRT terminal aesthetic.
- **Stack:** Qwen2.5-1.5B (default) via HF Inference API + procedural fallback engine

## Work Guidance

### TODO

> Keep tasks atomic and testable.

#### In Progress

- [ ] Test CritterCalm voice cloning pipeline end-to-end
- [ ] Test FocusFriend all 4 modes (Chat, Focus, Breathe, Meditate) with real model
- [ ] Record demo videos (2-3 min each)
- [ ] Post to social media
- [ ] Write Field Notes blog posts (3 — one per project)
- [ ] Share agent traces to HF Hub (Sharing is Caring badge)

#### Completed

- [x] CritterCalm v1 code complete (11 files) — Cedar-copper UI
- [x] FocusFriend v1 code complete (16 files) — Cedar-copper UI + Gradio 6 dict Chatbot
- [x] TinyBard v1 code complete (8 files) — LLM + procedural fallback, CRT UI, clean FastAPI JSON
- [x] GitHub repos created (nbiish/crittercalm, nbiish/focusfriend, nbiish/tinybard)
- [x] HF Spaces created and deployed (all 3)
- [x] Monorepo structure with projects/ directory + shared/ aesthetic module
- [x] INTELLIGENCE.md — full hackathon landscape analysis
- [x] SUBMISSION_DRAFTS.md — social posts + Field Notes drafts
- [x] HF CLI installed + skills configured (`hf skills add --global`)
- [x] llama-cpp-python installed (conda-forge v0.3.16) — for reference; v0.5+ uses HF Inference API
- [x] Local verification: all 3 apps run on ports 7861/7862/7863
- [x] TinyBard end-to-end game loop verified (start → choose → next scene)
- [x] FocusFriend chat verified (user message → Pip reply)
- [x] CritterCalm UI navigation verified (all 3 tabs render)
- [x] **v0.5: HF Inference API wired into all 3 apps** (no local GGUF, no build step)
- [x] **v0.5: Cooldown system** in `shared/inference_client.py` to protect HF/Modal credit budget
- [x] **v0.5: TinyBard local test** — procedural fallback works when no HF_TOKEN; cooldown UI shows in footer

### Short-term Goals

- Iterate on the live HF Spaces (nbiish/tinybard, nbiish/focusfriend, nbiish/crittercalm)
- Set HF_TOKEN + INFERENCE_MODEL Space secrets to enable real LLM-backed adventures
- Record demo videos and post to social media
- Write and publish Field Notes blog posts
- Share agent traces for Sharing is Caring badge
- Polish UIs for demo appeal

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning `llms.txt` when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- `llms.txt` creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root `llms.txt` is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child `llms.txt` files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

- Create a child `llms.txt` when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:
- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Put broad rules in parent docs and concrete details in child docs
- Prefer direct bullets with explicit names
- Do not duplicate rules across many files unless each scope needs a local version
- Delete stale notes instead of explaining history
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why

## Verification

Run local servers to verify apps:
- TinyBard: `cd projects/tinybard && python app.py` → http://localhost:7861/
- FocusFriend: `cd projects/focusfriend && python app.py` → http://localhost:7862/
- CritterCalm: `cd projects/crittercalm && python app.py` → http://localhost:7863/

## Reference

- CritterCalm: projects/crittercalm/ + github.com/nbiish/crittercalm
- FocusFriend: projects/focusfriend/ + github.com/nbiish/focusfriend
- TinyBard: projects/tinybard/ + github.com/nbiish/tinybard
- Aesthetic module: shared/cedar_copper_tokens.py
- Inference client: shared/inference_client.py
- ML Intern: github.com/huggingface/ml-intern
- HF Agents CLI: huggingface.co/docs/hub/en/agents-cli
- Gradio MCP: gradio.app/guides/model-context-protocol

## User Preferences

When the user requests a durable behavior change, record it here or in the relevant child `llms.txt`

## Child DOX Index

### projects/crittercalm/
- Backyard AI track — CritterCalm wildlife sound identifier
- Stack: OmniVoice + Dolphin-X1-8B + Kokoro TTS

### projects/focusfriend/
- Thousand Token Wood track — FocusFriend productivity assistant
- Stack: Gemma 4 12B via llama-cpp-python

### projects/tinybard/
- Thousand Token Wood + Tiny Titan + Llama Champion tracks
- Stack: VibeThinker 1.5B + procedural fallback

### shared/
- Cedar-copper aesthetic tokens and shared utilities
