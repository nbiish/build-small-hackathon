# Build Small Hackathon — Complete Reference

**Source:** https://huggingface.co/spaces/build-small-hackathon/README/blob/main/README.md  
**Organization:** https://huggingface.co/build-small-hackathon  
**Discord:** https://discord.gg/YHECTft87Z

---

## 📅 Timeline

| Phase | Date | Status |
|-------|------|--------|
| Registration | May 7 – June 3, 2026 | ✅ Closed |
| Hack Window | June 5 – June 15, 2026 | 🟢 **LIVE NOW** |
| Mid-window AMA | TBD | Upcoming |
| Submissions Close | June 15, 2026 | Deadline |
| Winners Announced | TBD | After judging |

---

## 🎯 Two Tracks — Pick One

### 🏡 Track 1: Backyard AI
**Solve a real problem for someone you actually know.**
- Pick a person: neighbor, parent, small-business owner
- Build something that makes their day measurably better

**Judged on:**
- ✦ Problem is specific and real
- ✦ The person actually used it
- ✦ Honest fit between problem and small-model constraint
- ✦ Polish of the Gradio app

### 🍄 Track 2: An Adventure in Thousand Token Wood
**Build something delightful that wouldn't exist without AI.**
- A toy, tiny game, strange interactive story, art experiment
- The AI should be doing the fun thing — not just helping you build it
- Strange is good. Joyful is the bar.

**Judged on:**
- ✦ Genuinely delightful (would you show a friend?)
- ✦ AI is load-bearing for the experience
- ✦ Originality of concept
- ✦ Polish of the Gradio app

---

## 📏 Three Hard Constraints

| # | Rule | Details |
|---|------|---------|
| 1 | **Small Models Only** | Total parameters ≤ 32 billion. Must fit on a laptop. |
| 2 | **Built on Gradio** | Your app must be a Gradio app, hosted as a Hugging Face Space. |
| 3 | **Show, Don't Tell** | Short demo video + social media post required for submission. |

---

## 🏅 Bonus Quests (Merit Badges) — Extra Points

| Badge | Name | Requirement |
|-------|------|-------------|
| 🔌 | **Off the Grid** | No cloud APIs. Entirely local-first. |
| 🎯 | **Well-Tuned** | Uses a fine-tuned model you've published on Hugging Face. |
| 🎨 | **Off-Brand** | Custom frontend pushing past default Gradio look (use `gr.Server`). |
| 🦙 | **Llama Champion** | Model runs through llama.cpp runtime. |
| 📡 | **Sharing is Caring** | Shared agent trace on the Hub for everyone to learn from. |
| 📓 | **Field Notes** | Wrote a blog post/report about what you built and learned. |

---

## 💰 Prize Pool: $48,000+ Cash & Physical Prizes

### Main Track Awards — $18,000

| Track | 1st | 2nd | 3rd | 4th |
|-------|-----|-----|-----|-----|
| **Backyard AI** | $4,000 | $2,500 | $1,500 | $1,000 |
| **Thousand Token Wood** | $4,000 | $2,500 | $1,500 | $1,000 |

### Community Choice — $2,000
- One winner, voted by the community

### Sponsor Awards

| Sponsor | Prize |
|---------|-------|
| **OpenBMB** | $10,000 total — 3 prizes per track (1st: $2,500, 2nd: $1,500, 3rd: $1,000) |
| **OpenAI** | $10,000 total — 1st: $5,000, 2nd: $3,000, 3rd: $2,000 |
| **NVIDIA** | 2× RTX 5080 GPUs for standout Nemotron builds |
| **Modal** | $20,000 credits — 1st: $10k, 2nd: $7k, 3rd: $3k |
| **Cohere** | $5,000 cash to prize pool |
| **JetBrains** | $5,000 cash to prize pool |
| **Black Forest Labs** | $3,000 cash to prize pool |

### Special Awards — $8,000

| Award | Prize |
|-------|-------|
| **Bonus Quest Champion** | $2,000 — Most merit badges on a single submission |
| **Off-Brand Award** | $1,500 — Best custom UI past default Gradio |
| **Tiny Titan** | $1,000 — Best app on ≤4B parameter model |
| **Best Demo** | $1,500 — Full package: great video + social post |
| **Community Favorite** | $2,000 — Voted by participants |

---

## 🛠 Tools & Resources for the Trail

| Resource | Link |
|----------|------|
| ML Intern (starter kit) | https://github.com/huggingface/ml-intern |
| Gradio Guides | https://www.gradio.app/guides/quickstart |
| Gradio `gr.Server` (custom UI) | https://huggingface.co/blog/introducing-gradio-server |
| Llama.cpp Getting Started | https://github.com/ggml-org/llama.cpp |
| Hackathon Org (submit Spaces here) | https://huggingface.co/build-small-hackathon |

---

## 📋 Submission Checklist (Due June 15)

- [ ] Gradio app hosted as a **Hugging Face Space** under the `build-small-hackathon` org
- [ ] Model ≤ 32B parameters (verify in Space config)
- [ ] **Demo video** (short, shows the app working)
- [ ] **Social media post** (tweet, LinkedIn, etc. — link in submission)
- [ ] Space link submitted via the org

---

## 🔑 Per-Participant Credits (Just for Registering)

| Provider | Credit |
|----------|--------|
| OpenAI Codex | $100 (first 1,000 participants) |
| Modal | $250 |
| Hugging Face | $20 |

---

## 💡 Project Ideas Brainstorming

### Backyard AI Track Ideas
- **Local recipe organizer** for a parent who prints recipes from websites
- **Inventory tracker** for a neighbor's small craft business
- **Medication reminder** with voice for an elderly relative
- **Garden planting calendar** customized to local climate zone
- **Homework helper** for a specific subject a kid struggles with
- **Accessibility tool** for someone with specific needs (voice-to-text, high contrast, etc.)

### Thousand Token Wood Track Ideas
- **Interactive micro-fiction** where the model co-writes a strange story
- **Tiny text adventure** with AI-generated rooms/NPCs
- **AI art collaborator** — you draw a blob, it completes it into something weird
- **Dream interpreter** that generates surreal illustrations
- **Procedural poem generator** with strange constraints
- **AI dungeon master** for a 5-minute solo RPG session
- **Glitch poetry** — model corrupts/transforms text in artistic ways

---

## ⚡ Quick Start Commands

```bash
# Clone the hackathon org (for reference)
git clone https://huggingface.co/build-small-hackathon

# Create a new Gradio Space locally
# Then push to: https://huggingface.co/build-small-hackathon/your-space-name

# Test model size (example)
python -c "
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained('model-name')
print(f'Parameters: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B')
"
```

---

## 📝 Notes for Our Team

- **We're in the hack window (June 5-15)** — build time is NOW
- **Two weekends** to build, ship, and demo
- **Gradio Space must be under the org** — not personal account
- **Model size is HARD constraint** — verify before submitting
- **Bonus quests stack** — aim for multiple badges for extra points
- **Demo video + social post are mandatory** — don't leave for last minute

---

*Last updated: 2026-06-07 | Source: Hugging Face Spaces README*