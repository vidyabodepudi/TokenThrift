# Token Thrift 🪙

**Universal output token compression skill for any LLM.**

Reduce output token costs by 25-75% across ChatGPT, Claude, Gemini, Kimi K2.5,
Qwen, GLM, DeepSeek, Llama, and any other LLM that accepts system prompts.

## Why

LLMs are verbose by default. RLHF training teaches them to be polite, add
preambles, restate questions, hedge their answers, and offer follow-up help.
Every word costs tokens. Every token costs money (or quota).

Token Thrift provides battle-tested system prompts that cut the fluff while
preserving technical accuracy — with adaptive intelligence that knows *when*
to compress and when to let the model think freely.

### NOTE

TokenThrift will NOT reduce your usage against a quota or billing. It just cuts the noise on output so you can se the reasoning clearly. This was just a fun project to see if it was useful or not. TLDR: Its useful to some people. 

## Quick Start

1. Pick a compression level:
   - **L1 Trim** (~30% savings) — Safe for all tasks
   - **L2 Compress** (~50% savings) — Great for developer workflows
   - **L3 Crush** (~70% savings) — Maximum savings for action tasks
   - **Adaptive** (~40% savings, 0% accuracy risk) — Recommended starting point

2. Copy the system prompt from `prompts/L1_trim.md`, `L2_compress.md`,
   `L3_crush.md`, or `references/adaptive_modes.md`

3. Paste it into your LLM's system message

4. Optionally apply per-model tuning from `tuning/model_specific.md`

## Structure

```
token-thrift/
├── SKILL.md                          # Main skill definition & architecture
├── README.md                         # This file
├── prompts/
│   ├── L1_trim.md                    # Light compression (25-35%)
│   ├── L2_compress.md                # Medium compression (40-55%)
│   └── L3_crush.md                   # Maximum compression (60-75%)
├── tuning/
│   └── model_specific.md             # Per-model overrides & tips
├── references/
│   ├── adaptive_modes.md             # Smart mode-switching system prompt
│   ├── structural_optimization.md    # JSON/YAML/TOON/tables/stop sequences
│   └── token_tracking_template.md    # Track your savings over time
└── scripts/
    └── estimate_tokens.py            # Measure token counts & compare
```

## Key Design Decisions

### Format, not Persona
We constrain *how the model formats its output*, not *how it thinks*.
Research shows that forcing an LLM to "talk like a caveman" or adopt a
low-IQ persona degrades reasoning quality (Tam et al., EMNLP 2024).
Token Thrift says "be concise" — not "be dumb".

### Adaptive over Uniform
Blind compression of everything hurts reasoning tasks. The adaptive mode
system detects task type and applies compression selectively: aggressive
on action tasks (where verbosity is pure waste), gentle on reasoning tasks
(where the model needs expressive room).

### Layered Architecture
Three compression layers (linguistic → structural → semantic) let you
dial in exactly the right level for your use case. They compound.

## Measuring Results

```bash
# Install the tokenizer
pip install tiktoken

# Count tokens
python scripts/estimate_tokens.py "your text here"

# Compare before/after
python scripts/estimate_tokens.py --compare before.txt after.txt

# Interactive mode
python scripts/estimate_tokens.py --interactive
```

## Research References

- Tam et al. (2024). "Let Me Speak Freely? A Study On The Impact Of Format
  Restrictions On Large Language Model Performance." EMNLP Industry Track.
  https://aclanthology.org/2024.emnlp-industry.91/

- Chain of Draft: Concise intermediate reasoning steps (≤5 words per step)
  that maintain accuracy while dramatically reducing output tokens.

## License

Apache 2.0 — Do things, compress freely.
