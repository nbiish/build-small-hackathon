---
name: ml-intern
description: "Hugging Face ML Intern CLI (`ml-intern`) — an agent that turns natural-language goals into end-to-end ML workflows using the HF ecosystem. Use when: the user wants to research papers/datasets, fine-tune models, run ML experiments, publish artifacts to HF Hub, or perform any multi-step ML engineering task. Combines research, code generation, sandbox execution, and Hub publishing. Use with `hf` CLI for deterministic repo/space/job operations."
---

# ML Intern Skill

## What is ml-intern?

`ml-intern` is a CLI-first agent from Hugging Face that orchestrates end-to-end ML workflows:
- Research papers and docs via HF Hub
- Inspect and query datasets
- Write training/evaluation code
- Run experiments locally or in HF sandbox (GPU-backed)
- Publish models, datasets, and Spaces to HF Hub

**Source**: https://github.com/huggingface/ml-intern

## When to Use

| Use `ml-intern` | Use `hf` CLI | Use both |
|---|---|---|
| Broad ML engineering task | Precise Hub/Space/Jobs commands | Agent-driven workflow + deterministic ops |
| Research → plan → train → eval → publish | Upload/download files | Train locally, publish via `hf upload` |
| Multi-step experimentation | Check model/dataset info | Research via ml-intern, deploy via `hf` |
| "Fine-tune X on my dataset" | "List my models" | "Train then push to Hub" |

## Prerequisites

### Install

```bash
git clone https://github.com/huggingface/ml-intern.git
cd ml-intern
uv sync
uv tool install -e .
```

### Required Environment Variables

```bash
HF_TOKEN=<your-hugging-face-token>
GITHUB_TOKEN=<github-personal-access-token>
```

Optional (only for closed providers):
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

**Secrets management**: Use PQC secrets bundle (`~/.config/pqc-secrets/`) or `secrets-load` shell function. Never commit tokens to repo files.

## Basic Usage

```bash
# Interactive mode
ml-intern

# Goal-directed mode
ml-intern "fine-tune llama on my dataset"

# With sandbox (GPU-backed remote execution)
ml-intern --sandbox-tools "test this training script in a GPU sandbox"

# Limit iterations
ml-intern --max-iterations 100 "your prompt"

# Non-streaming output
ml-intern --no-stream "your prompt"
```

## Model Selection

```bash
# Default (HF Inference)
ml-intern "your prompt"

# Specific HF model
ml-intern --model moonshotai/Kimi-K2.6 "your prompt"

# Closed provider
ml-intern --model openai/gpt-5.5:fal-ai "your prompt"

# Local models
ml-intern --model ollama/llama3.1:8b "your prompt"
ml-intern --model vllm/meta-llama/Llama-3.1-8B-Instruct "your prompt"
ml-intern --model lm_studio/google/gemma-3-4b "your prompt"
ml-intern --model llamacpp/llama-3.1-8b-instruct "your prompt"
```

Interactive model switch during session:
```
/model ollama/llama3.1:8b
```

## Built-in Tools

ml-intern routes to these tool groups:

| Tool | Purpose |
|---|---|
| Research sub-agent | Deep topic investigation |
| HF docs search/fetch | Official documentation lookup |
| HF papers | Academic paper search and reading |
| Web search | General web research |
| Dataset inspection | `hf datasets info`, parquet queries |
| Planning + notifications | Workflow orchestration |
| HF Jobs | Run compute on HF infrastructure |
| HF repo files/git | Repo file management |
| GitHub code search | Find implementation examples |
| Sandbox tools | Remote GPU execution |
| Local tools | Filesystem read/write/edit |

## Workflows

### Standard ML Workflow

```
Research → Plan → Inspect Data → Write Code → Train → Evaluate → Publish
```

### Local Mode vs Sandbox Mode

**Local mode** (`bash`, `read`, `write`, `edit`):
- Direct filesystem inspection
- Local repo checkout iteration
- No remote compute costs

**Sandbox mode** (HF Space sandbox + GPU):
- Remote isolation
- GPU-backed training
- Disposable execution environments
- Requires HF Jobs access

### Approval Gates

ml-intern has built-in approval for sensitive operations:
- `approval_required` events pause the loop
- Human must confirm before: destructive file ops, Hub publishes, compute job launches
- This is a safety feature, not a bug

## Integration with HF CLI

Pair ml-intern with `hf` for deterministic operations:

```bash
# ml-intern handles research + code generation
ml-intern "write a training script for sentiment analysis"

# hf handles precise Hub operations
hf upload myorg/sentiment-model ./output

# hf handles Space deployment
hf repos create myorg/sentiment-demo --type space --space-sdk gradio
hf upload myorg/sentiment-demo ./app.py

# hf handles Jobs
hf jobs run pytorch/pytorch:latest "python train.py" --flavor t4-small
```

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Stalled on approval | Approval gate waiting | Check terminal for `approval_required` event |
| Token scope error | HF_TOKEN lacks permissions | `hf auth login` with write token |
| Sandbox timeout | GPU queue busy | Retry or use `--flavor` for different hardware |
| MCP tool error | External MCP server down | Check MCP server status, restart ml-intern |
| Stale tools | Tool cache issue | Restart ml-intern session |

## Security Notes

- Token scoping: use fine-grained tokens with minimal permissions
- Sandbox mode is safer for untrusted code (isolated execution)
- Local mode has full filesystem access — trust the code before running
- Never commit `.env` files with tokens
- Use PQC secrets bundle for production token management

## Quick Reference

```bash
ml-intern                              # Interactive mode
ml-intern "goal"                       # Goal-directed
ml-intern --sandbox-tools "goal"       # With GPU sandbox
ml-intern --max-iterations N "goal"    # Limit iterations
ml-intern --model MODEL "goal"         # Specific model
ml-intern --no-stream "goal"           # Non-streaming
```
