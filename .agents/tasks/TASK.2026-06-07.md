# CritterCalm — Build Task

**Branch:** feat/crittercalm-animal-voice-soother
**Worktree:** ../crittercalm
**Track:** Backyard AI
**Date:** 2026-06-07

## Chain-of-Draft

1. Scaffold: mkdir voice_cloning content utils
2. Write app.py — 3-tab Gradio Blocks
3. OmniVoice wrapper — lazy-load, clone, cache embed
4. Dolphin-X1-8B script gen — system prompt, template fallback
5. Kokoro TTS fallback — built-in voices
6. Pre-written templates — 6 animals × 8 situations × scripts
7. Audio utils — load, save, validate, duration
8. requirements.txt + README.md
9. Wire imports across modules
10. Verify: all deps resolve, app launches

####

## Deliverables
- [x] app.py — Main Gradio app (3 tabs)
- [x] voice_cloning/ — OmniVoice integration
- [x] content/ — Script generation + templates
- [x] utils/ — Audio processing
- [x] requirements.txt
- [x] README.md
- [ ] Deploy to HF Spaces
- [ ] Demo video
- [ ] Social post
