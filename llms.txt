# ◈──◆──◇ ANISHINAABE-MOWIN / OBIJWE BUILD SMALL HACKATHON — PRD ◇──◆──◈
# Project Requirements Document

> **ᐴ Three Gradio apps targeting all tracks + maximum badges + sponsor prizes. ᔔ**
> Hack window: June 5-15, 2026. Deadline: June 15.
> **Aaniin. Miigwech.** — We honor the Anishinaabe-Aki where these apps were built.

---

## ᐴ WAAWIINDAMAAGEWIN ᔔ [OVERVIEW] ◈──◆──◇──◆──◈

- **Name:** Build Small Hackathon 2026 — Team nbiish
- **Version:** 0.4.0 — Anishinaabe Solarpunk Edition
- **Description:** Multi-project hackathon entry targeting $48K+ prize pool across Backyard AI and Thousand Token Wood tracks. Three Gradio apps using small models (≤32B) with maximum bonus badge coverage.
- **Aesthetic:** Anishinaabe Solarpunk — sky-to-sunrise palette (water-blue → cedar → copper → sun-amber → birch-cream), Canadian Aboriginal Syllabics (ᐴ, ᔔ, ☼, ☘, ❀) as section framings, biophilic motifs.
- **Purpose:** Win prizes across tracks, badges, and sponsor categories by building delightful, useful AI apps that run locally.
- **UX:** Gradio web apps (gr.Blocks + mount_gradio_app custom frontends), hosted on HF Spaces.
- **Shared tokens module:** `shared/anishinaabe_solarpunk.py` — design tokens reusable across all 3 apps.

---

## ᐴ WAAJA'INIDIZOWIN ᔔ [RULES] ◈──◆──◇──◆──◈

### ☼ GANAWENDAAGWAD / NAMING & COMMENTS ◈

- Descriptive project names: CritterCalm, FocusFriend, TinyBard
- Docstrings on all public functions. Comments on non-obvious logic.
- Bilingual English + Anishinaabemowin where natural (without appropriation — use Aaniin for greetings, descriptive terms for features).

### ☼ ZHOONIYAA / ALWAYS ◈

- Models ≤ 32B total params per project
- Gradio app hosted as HF Space
- Local-first (no cloud APIs = Off the Grid badge)
- GGUF quantized models for local inference
- Python 3.10+ with pinned requirements
- Anishinaabe Solarpunk aesthetic consistency across all UIs

### ☼ GIGAANAN / NEVER ◈

- Cloud API calls in production path
- Hardcoded secrets or API keys
- Models > 32B params
- Default Gradio look without customization attempt

### ☼ INA-ENDAWAAZOWINAN / IF ◈

- If custom frontend is feasible → use mount_gradio_app for Off-Brand badge
- If model ≤ 4B → tag Tiny Titan eligible
- If using llama.cpp runtime → tag Llama Champion
- If fine-tuning is done → publish model to HF Hub

---

## ᐴ NITAM-AABAJICHIGANAN ᔔ [INFRASTRUCTURE] ◈──◆──◇──◆──◈

### ☼ GRADIO 6.0 + MCP SERVER ◈

- `gradio.Server` is **NOT** in Gradio 6.0 stable. Use `mount_gradio_app(fastapi_app, blocks, path="/gradio")` instead.
- MCP server mode: `demo.launch(mcp_server=True)` or `GRADIO_MCP_SERVER=true` env var.
- Custom frontends: Serve static HTML/CSS/JS via FastAPI, mount Gradio at `/gradio` for API + MCP.
- `@gradio/client` CDN: `https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js` (ES module, use `type="module"`).
- Theme parameters: `css`, `head`, `theme` moved from `gr.Blocks(...)` to `app.launch(...)` in Gradio 6.0.
- Chatbot API: Gradio 6.0 requires `{"role": "user|assistant", "content": "..."}` dicts (not tuples).

### ☼ HF AGENTS CLI ◈

- `hf` CLI is installed (v1.18.0). See `skill://hf-cli` for full command reference.
- Install expert skills: `hf skills add --global` or `hf skills add --claude --global`.
- Spaces managed via: `hf repos create <name> --type space --space-sdk gradio --public`.
- Deploy: `git remote add hf https://huggingface.co/spaces/<user>/<space>` then `git push hf main`.
- HF README metadata: `colorTo` must be one of `[red, yellow, green, blue, indigo, purple, pink, gray]` (no `emerald`/`amber`).

### ☼ ZHOONIYAAWICHIGEWIN / LOCAL TEST ENVIRONMENT ◈

- Python: miniconda3 (Python 3.12)
- Gradio: 6.0.0
- llama-cpp-python: installed via conda-forge (v0.3.16)
- Available GGUF models:
  - VibeThinker-1.5B.Q8_0.gguf (in HF cache)
  - LFM2-1.2B-Q4_K_M.gguf (in HF cache)
  - LFM2-8B-A1B-Q4_K_M.gguf (in ggufy/models/)
- Missing GGUF models (need download): Gemma 4 12B, Dolphin-X1-8B

### ☼ AABAJICHIGANAN / LOCAL SERVERS ◈

All 3 apps run simultaneously on different ports for visual inspection:

| Project | URL | Stack | HF Space |
|---|---|---|---|
| TinyBard | http://localhost:7861/ | FastAPI + Gradio Blocks | nbiish/tinybard |
| FocusFriend | http://localhost:7862/ | Gradio 6.0 | nbiish/focusfriend |
| CritterCalm | http://localhost:7863/ | Gradio 6.0 | nbiish/crittercalm |

---

## ᐴ INA-WAABANDA'IWEWINAN ᔔ [PROJECTS] ◈──◆──◇──◆──◈

### ☼ 1. CRITTERCALM — Maanamewin / Voice-Comfort for the Four-Leggeds ◈

- **Status:** Code complete. Deployed. Locally tested. Anishinaabe-Solarpunk UI applied.
- **Stack:** OmniVoice (0.6B) + Dolphin-X1-8B (8B) + Kokoro TTS (82M) = 8.7B params
- **Badges:** Off the Grid, Well-Tuned (TBD), Field Notes, Llama Champion (TBD), Off-Brand (custom banner)
- **GitHub:** github.com/nbiish/crittercalm
- **HF Space:** huggingface.co/spaces/nbiish/crittercalm
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/crittercalm-repo

### ☼ 2. FOCUSFRIEND — Pip, your cedar-and-sun companion on the lake ◈

- **Status:** Code complete. Deployed. Locally tested. Anishinaabe-Solarpunk UI applied. Gradio 6 Chatbot dict-format fixed.
- **Stack:** Gemma 4 12B (12B) via llama-cpp-python
- **Badges:** Off-Brand (sun-amber custom theme), Off the Grid, Field Notes
- **GitHub:** github.com/nbiish/focusfriend
- **HF Space:** huggingface.co/spaces/nbiish/focusfriend
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/focusfriend-repo
- **Note:** Gemma 4 12B GGUF not yet downloaded. Need `huggingface-cli download unsloth/gemma-4-12b-it-GGUF --include "gemma-4-12b-it-Q4_K_M.gguf" --local-dir ./models`

### ☼ 3. TINYBARD — Aanishinaabe Mikinaak-Aki / Fire-Fly Storyteller ◈

- **Status:** Code complete. Deployed. Locally tested end-to-end (game loop). Anishinaabe-Solarpunk CRT UI applied.
- **Concept:** ≤4B LLM generates 5-min interactive text adventures in a CRT terminal aesthetic.
- **Stack:** VibeThinker 1.5B (1.5B) via llama-cpp-python + procedural fallback engine
- **Architecture:** FastAPI + mount_gradio_app at /gradio. Custom HTML/CSS/JS frontend. MCP tools: start_game, make_choice.
- **Bilingual UI labels:** NOOSISKAAZOWIN (health), MII-GIIWETA (connected), AADIZOOKAAN (fantasy), ISHPIMING (sci-fi), MASHKODEWAAZIBI (cyberpunk).
- **Badges:** Llama Champion, Tiny Titan (1.5B < 4B), Off-Brand (custom CRT), Off the Grid, Field Notes
- **Prize targets:** Tiny Titan ($1K), Thousand Token Wood track, Bonus Quest Champion potential
- **GitHub:** github.com/nbiish/tinybard
- **HF Space:** huggingface.co/spaces/nbiish/tinybard
- **Standalone repo:** /Volumes/1tb-sandisk/code-external/tinybard

---

## ᐴ INAABAJICHIGANAN ᔔ [TODO] ◈──◆──◇──◆──◈

> Keep tasks atomic and testable.

### ☼ MAAJITAAWIN / IN PROGRESS ◈

- [x] ~~Download Gemma 4 12B and Dolphin-X1-8B GGUF models~~ → blocked: not yet in dev plan
- [ ] Test CritterCalm voice cloning pipeline end-to-end
- [ ] Test FocusFriend all 4 modes (Chat, Focus, Breathe, Meditate) with real model
- [ ] Record demo videos (2-3 min each)
- [ ] Post to social media
- [ ] Write Field Notes blog posts (3 — one per project)
- [ ] Share agent traces to HF Hub (Sharing is Caring badge)

### ☼ GIIZHIITAA / COMPLETED ◈

- [x] CritterCalm v1 code complete (11 files) — Anishinaabe-Solarpunk UI
- [x] FocusFriend v1 code complete (16 files) — Anishinaabe-Solarpunk UI + Gradio 6 dict Chatbot
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

## ᐴ NITAAM-AADIZOOKAAN ᔔ [SHORT-TERM GOALS] ◈──◆──◇──◆──◈

- Test all 3 apps locally with real GGUF models (currently running with procedural fallbacks)
- Record demo videos and post to social media
- Write and publish Field Notes blog posts
- Share agent traces for Sharing is Caring badge
- Sync aesthetic updates to standalone GitHub repos + HF Spaces (push)

---

## ᐴ INA-WAABANDA'IWEWIN ᔔ [REFERENCE] ◈──◆──◇──◆──◈

- CritterCalm: projects/crittercalm/ + github.com/nbiish/crittercalm
- FocusFriend: projects/focusfriend/ + github.com/nbiish/focusfriend
- TinyBard: projects/tinybard/ + github.com/nbiish/tinybard
- Aesthetic module: shared/anishinaabe_solarpunk.py
- ML Intern: github.com/huggingface/ml-intern
- HF Agents CLI: huggingface.co/docs/hub/en/agents-cli
- Gradio MCP: gradio.app/guides/model-context-protocol
- Anishinaabe-Solarpunk styling guide: skill://anishinaabe-cyberpunk-style

---

◈──◆──◇ ☼ Anishinaabe Solarpunk Edition · Cedar Edition · v0.4.0 ◇──◆──◈
