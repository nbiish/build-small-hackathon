# Build Small Hackathon — Full Intelligence Dump
# Compiled 2026-06-08

## New Resources (not in original HACKATHON_README.md)

### gr.Server — True Custom Frontends (Off-Brand Badge Key)
- **Blog:** https://huggingface.co/blog/introducing-gradio-server
- **Docs:** https://www.gradio.app/main/guides/server-mode
- `gradio.Server` inherits from FastAPI — you can serve ANY HTML/CSS/JS frontend
  while keeping Gradio's queuing, concurrency, SSE streaming, and ZeroGPU support.
- Frontend connects via `@gradio/client` JS library using `client.predict()`
- This is the REAL Off-Brand path — not just custom CSS on gr.Blocks
- **Action:** Upgrade FocusFriend to gr.Server with a fully custom vanilla HTML/JS frontend

### ML Intern — Autonomous ML Agent
- **Repo:** https://github.com/huggingface/ml-intern
- Autonomous agent that researches, writes, and ships ML code using HF ecosystem
- Can be used WITH our projects for Sharing is Caring badge (agent traces)
- CLI tool: `ml-intern "build a TTS app"` — it researches and codes autonomously
- **Action:** Run ml-intern on our projects, share traces to Hub

### gr.Server Code Pattern (for FocusFriend upgrade)
```python
from gradio import Server
from fastapi.responses import HTMLResponse

app = Server()

@app.api(name="chat")
def chat_endpoint(message: str, history: list) -> dict:
    # LLM inference here
    return {"response": "...", "mood": "focus"}

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("index.html") as f:
        return f.read()

app.launch()
```

Frontend (index.html) uses vanilla HTML/CSS/JS + @gradio/client library:
```javascript
import { Client } from "@gradio/client";
const client = await Client.connect(window.location.origin);
const result = await client.predict("/chat", { message, history });
```

---

## Competition Landscape — What's Already Submitted

### Spaces in the Org (213 total — 6 sampled)
| Space | Concept | Track |
|-------|---------|-------|
| mind-of-tashi | AI consciousness sim | Thousand Token Wood |
| vivamais | Health/wellness AI | Backyard AI |
| split-brain-copilot | Dual-perspective AI assistant | Thousand Token Wood |
| lolaby | Lullaby/audio generation | Backyard AI |
| NPCverse | AI NPC dialogue system | Thousand Token Wood |
| museum-of-unlived-lives | Generative art/storytelling | Thousand Token Wood |

### Models Published (32 total)
Notable fine-tunes (proving Well-Tuned badge is achievable):
- mind-of-tashi-micro-grpo (GRPO fine-tune)
- NeuroBait
- flux-costume-booth-lora (LoRA for Flux)
- tiny-quest-radio-aya-lora (LoRA fine-tune)
- pocket-tutor-minicpmv-socratic

### Datasets Published (22 total) — Sharing is Caring in action
- mind-of-tashi-runs (agent traces)
- 1000-Rooms-traces
- hackathon-advisor-codex-traces
- bedtime-story-machine-trace
- jawbreaker-scam-defense-data

### Blog Posts (12 Field Notes examples)
- ClinIQ: On-device pharmacist
- Thousand Token Wood sim v2/v3
- Building Pakistan Notice Helper
- Amazing Digital Dentures
- Room360: Video to 3D reconstruction
- Mythograph Atelier
- Her · हेर
- Job Searcher
- Persona Atlas

---

## Gap Analysis — What We Haven't Covered

### Badges NOT Yet Targeted
| Badge | Status | How to Get It |
|-------|--------|---------------|
| 🦙 Llama Champion | ❌ | Need to run model through llama.cpp runtime directly (not just llama-cpp-python) |
| 📡 Sharing is Caring | ❌ | Need to publish agent traces to HF Hub |
| 🎨 Off-Brand (true) | ⚠️ Partial | FocusFriend has custom CSS but should use gr.Server for full custom frontend |
| 🎯 Well-Tuned | ❌ | Need to actually fine-tune and publish a model |

### Sponsor Prizes NOT Targeted
| Sponsor | Prize | How to Target |
|---------|-------|---------------|
| NVIDIA | 2× RTX 5080 | Build with Nemotron models |
| Cohere | $5K cash | Use Cohere models (Command R, etc.) |
| Black Forest Labs | $3K cash | Use Flux image models |
| Modal | $20K credits | Deploy on Modal infrastructure |

### Special Awards NOT Targeted
| Award | Prize | How to Target |
|-------|-------|---------------|
| Tiny Titan | $1,000 | App using ≤4B param model |
| Bonus Quest Champion | $2,000 | Most badges on single submission |
| Best Demo | $1,500 | Best video + social post package |

---

## Third Project Ideas — Fill the Gaps

### Option A: "Tiny Bard" — Micro-Adventure Generator
- **Track:** Thousand Token Wood
- **Model:** Qwen 2.5 1.5B or Phi-4-mini (3.8B) — Tiny Titan eligible
- **Runtime:** llama.cpp (Llama Champion badge)
- **Concept:** Tiny LLM generates interactive text adventures. Each playthrough is 5 minutes.
  The AI creates rooms, NPCs, items, and branching narratives on the fly.
- **Frontend:** gr.Server with custom pixel-art/terminal UI
- **Badges:** 🦙 Llama Champion · 🏆 Tiny Titan · 🎨 Off-Brand · 🔌 Off the Grid · 📓 Field Notes
- **Prize targets:** Tiny Titan ($1K) · Thousand Token Wood ($4K-$1K) · Bonus Quest Champion potential

### Option B: "CritterCalm Mini" — Tiny Titan Edition
- **Track:** Backyard AI
- **Model:** Replace Dolphin-X1-8B with Qwen 2.5 1.5B — Tiny Titan eligible
- **Concept:** Slim version of CritterCalm that runs on ANY hardware. Just the calming templates + Kokoro TTS.
- **Badges:** 🏆 Tiny Titan · 🔌 Off the Grid
- **Effort:** Low (mostly repackaging existing work)

### Option C: "DreamSnap" — Surreal Pet Portrait Generator
- **Track:** Thousand Token Wood
- **Model:** Black Forest Labs Flux (small variant) + small LLM
- **Concept:** Describe your pet → generate surreal/delightful pet portraits. AI co-creates the art.
- **Badges:** 🎨 Off-Brand · 📓 Field Notes
- **Prize targets:** Black Forest Labs sponsor prize ($3K) · Thousand Token Wood

### Option D: "TraceShare" — Agent Trace Publisher
- **Concept:** Utility tool that helps ALL hackathon participants share agent traces easily
- **Use ML Intern** to generate traces, then publish to HF Hub
- **Badges:** 📡 Sharing is Caring (applied to multiple projects)
- **Effort:** Very low — just run ml-intern, capture traces, publish

---

## Recommended Action Plan (June 8-15)

### Priority 1: Upgrade Existing Projects
1. **FocusFriend → gr.Server** — Replace gr.Blocks with fully custom HTML/JS frontend
   - True Off-Brand badge qualification
   - Keep all existing Pip personality + mode logic
2. **CritterCalm → Add llama.cpp runtime** — Get Llama Champion badge
3. **Both → Share agent traces** — Run ml-intern, publish traces to Hub

### Priority 2: Quick Win — Tiny Titan
4. **Build "CritterCalm Mini"** — Slim version with ≤4B params
   - Same app structure, smaller model
   - Gets Tiny Titan award eligibility

### Priority 3: Third Project (if time permits)
5. **Build "Tiny Bard"** — Micro-adventure generator
   - Hits 5 badges at once (Llama Champion, Tiny Titan, Off-Brand, Off the Grid, Field Notes)
   - Strong Bonus Quest Champion candidate

---

## Updated Badge Strategy Per Project

### CritterCalm
| Badge | Status | Action |
|-------|--------|--------|
| 🔌 Off the Grid | ✅ Built local | Verify no API calls |
| 🎯 Well-Tuned | ⬜ | Fine-tune OmniVoice on pet-directed speech |
| 📓 Field Notes | ✅ Draft written | Polish and publish |
| 📡 Sharing is Caring | ⬜ | Run with ml-intern, publish traces |
| 🦙 Llama Champion | ⬜ | Add llama.cpp server mode option |

### FocusFriend
| Badge | Status | Action |
|-------|--------|--------|
| 🎨 Off-Brand | ⚠️ Partial | Upgrade to gr.Server custom frontend |
| 🔌 Off the Grid | ✅ Built local | Verify no API calls |
| 📓 Field Notes | ✅ Draft written | Polish and publish |
| 📡 Sharing is Caring | ⬜ | Run with ml-intern, publish traces |
| 🦙 Llama Champion | ⚠️ Partial | Already uses llama-cpp-python — add llama.cpp server flag |

### Tiny Bard (New)
| Badge | Status |
|-------|--------|
| 🦙 Llama Champion | ✅ llama.cpp native |
| 🏆 Tiny Titan | ✅ ≤4B model |
| 🎨 Off-Brand | ✅ gr.Server custom UI |
| 🔌 Off the Grid | ✅ Fully local |
| 📓 Field Notes | To write |

---

## Links Repository

### Hackathon Official
- Org: https://huggingface.co/build-small-hackathon
- Discord: https://discord.gg/YHECTft87Z
- README Space: https://huggingface.co/spaces/build-small-hackathon/README

### Tools & Kits
- ML Intern: https://github.com/huggingface/ml-intern
- Gradio Quickstart: https://www.gradio.app/guides/quickstart
- gr.Server Blog: https://huggingface.co/blog/introducing-gradio-server
- gr.Server Docs: https://www.gradio.app/main/guides/server-mode
- llama.cpp: https://github.com/ggml-org/llama.cpp

### Our Repos
- Monorepo: (this)
- CritterCalm: https://github.com/nbiish/crittercalm
- FocusFriend: https://github.com/nbiish/focusfriend

### Models We're Using
- OmniVoice: https://github.com/k2-fsa/OmniVoice
- Dolphin-X1-8B: https://huggingface.co/dphn/Dolphin-X1-8B-GGUF
- Gemma 4 12B: https://huggingface.co/unsloth/gemma-4-12b-it-GGUF
- Kokoro TTS: https://github.com/thewh1teagle/kokoro-onnx
