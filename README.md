---
title: ᐴ TinyBard ᔔ
emoji: ☀️
colorFrom: blue
colorTo: yellow
sdk: gradio
sdk_version: 6.0.0
app_file: projects/tinybard/app.py
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

# ◈──◆──◇ ANISHINAABE-MOWIN / OBIJWE BUILD SMALL HACKATHON ◇──◆──◈

> **ᐴ Team coordination for the Hugging Face Build Small Hackathon (June 5-15, 2026). ᔔ**
> Aaniin. Miigwech. We honor the Anishinaabe-Aki where these apps were built.

```
build-small-hackathon/
├── AGENTS.md              # Agent instructions & workflow
├── HACKATHON_README.md    # Full hackathon reference
├── SUBMISSION_DRAFTS.md   # Social posts + Field Notes drafts
├── llms.txt               # PRD (this is the authoritative product spec)
├── projects/
│   ├── crittercalm/       # 🐾  Maanamewin / Voice Cloning Animal Soother
│   ├── focusfriend/       # ☼  Pip, your cedar-and-sun companion
│   ├── tinybard/          # ☼  Fire-fly Storyteller · CRT Terminal
│   └── shared/
│       ├── cedar_copper_tokens.py  # ☼ Cedar-copper aesthetic tokens
│       └── inference_client.py        # ☼ HF Inference API + cooldowns
└── .agents/               # Skills & task tracking
```

## ☼ PROJECTS — ᐴ INA-WAABANDA'IWEWINAN ᔔ ◈

| Project | Track | Badges | GitHub | HF Space |
|---|---|---|---|---|
| 🐾 **CritterCalm** | Backyard AI | Off the Grid, Well-Tuned, Field Notes, Off-Brand | [nbiish/crittercalm](https://github.com/nbiish/crittercalm) | [nbiish/crittercalm](https://huggingface.co/spaces/nbiish/crittercalm) |
| ☼ **FocusFriend** | Thousand Token Wood | Off-Brand, Off the Grid, Field Notes | [nbiish/focusfriend](https://github.com/nbiish/focusfriend) | [nbiish/focusfriend](https://huggingface.co/spaces/nbiish/focusfriend) |
| ☼ **TinyBard** | Thousand Token Wood | Llama Champion, Tiny Titan, Off-Brand, Off the Grid, Field Notes | [nbiish/tinybard](https://github.com/nbiish/tinybard) | [nbiish/tinybard](https://huggingface.co/spaces/nbiish/tinybard) |

## ☼ AESTHETIC — ᐴ ANISHINAABE-SOLARPUNK ᔔ ◈

All three apps share a unified visual language:

- **Palette:** sky-to-sunrise — water-blue (`#1B4965`) → cedar-bark (`#3D2A2A`) → copper (`#8B3A1F`) → sun-amber (`#F2A93B`) → birch-cream (`#F5F1E8`)
- **Syllabics:** Canadian Aboriginal ᐴ / ᔔ used as section framings
- **Symbols:** ☼ sun · ☘ clover · ❀ florette · ◈ ◆ ◇ circuit diamonds
- **Typography:** EB Garamond serif headers + Inter sans + JetBrains Mono for terminal/UI
- **Tokens module:** `shared/anishinaabe_solarpunk.py` — used by TinyBard, FocusFriend, CritterCalm
- **Skill:** `skill://anishinaabe-cyberpunk-style`

## ☼ LOCAL SERVERS — ᐴ INA-AABAJICHIGANAN ᔔ ◈

| Project | URL | Port | Backend |
|---|---|---|---|
| TinyBard | http://localhost:7861/ | 7861 | FastAPI + Gradio Blocks mounted |
| FocusFriend | http://localhost:7862/ | 7862 | Gradio 6.0 |
| CritterCalm | http://localhost:7863/ | 7863 | Gradio 6.0 |

## ☼ QUICK LINKS — ᐴ AABAJICHIGANAN ᔔ ◈

- [Submission Checklist](HACKATHON_README.md#-submission-checklist-due-june-15)
- [Draft Posts & Field Notes](SUBMISSION_DRAFTS.md)
- [PRD / llms.txt](llms.txt)
- [Hackathon Discord](https://discord.gg/YHECTft87Z)

## ☼ REMAINING TASKS — ᐴ INA-ENDAWAAZOWINAN ᔔ ◈

- [ ] Download Gemma 4 12B and Dolphin-X1-8B GGUF models
- [ ] Test CritterCalm voice cloning end-to-end
- [ ] Test FocusFriend all 4 modes (Chat, Focus, Breathe, Meditate) with real model
- [ ] Record demo videos (2-3 min each)
- [ ] Post to social media
- [ ] Submit via HF org
- [ ] Fine-tune voice model (Well-Tuned badge)
- [ ] Share agent traces (Sharing is Caring badge)

---

◈──◆──◇ ☼ Cedar-Copper Edition · v0.5.1 · Anishinaabe Solarpunk ◇──◆──◈
