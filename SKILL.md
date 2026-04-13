---
name: token-thrift
description: |
  Reduce LLM output token usage by 40-75%. Use when user wants to minimize API costs,
  compress model output, reduce token consumption, enable "caveman mode", or apply
  token budgeting. Works across all major LLMs (GPT, Claude, Gemini, Kimi, Qwen, GLM, etc.).
---

# Token Thrift — Universal Output Token Compression Skill

## Purpose
Dramatically reduce output token consumption from any LLM by applying layered compression
strategies. This skill provides ready-to-use system prompts, per-model tuning guidance,
and a framework for adaptive verbosity that balances cost savings with response quality.

## When to Use
- User is on **API billing** and wants to reduce per-request costs
- User is on **usage quota** pricing and wants to stretch their allocation
- User wants **faster responses** (fewer tokens = lower latency)
- User asks for "caveman mode", "compressed output", "token budget", or similar

---

## Quick Start

### 1. Choose a Compression Level

| Level | Name | Approx. Savings | Best For |
|:------|:-----|:-----------------|:---------|
| L1 | **Trim** | ~25-35% | Professional contexts, documentation |
| L2 | **Compress** | ~40-55% | Developer workflows, API pipelines |
| L3 | **Crush** | ~60-75% | Cost-critical batch jobs, internal tooling |

### 2. Apply the System Prompt

Insert the appropriate system prompt block (from `prompts/` directory) into the model's
system message. All prompts are model-agnostic by default — see `tuning/` for per-model
overrides.

### 3. Combine with Structural Strategies

For maximum savings, pair a compression prompt with the structural techniques in
the [Structural Optimization Guide](references/structural_optimization.md).

---

## Architecture: The Three Compression Layers

```
┌─────────────────────────────────────────────┐
│  Layer 1: LINGUISTIC COMPRESSION            │
│  Drop filler, articles, pleasantries        │
│  Strip preamble/postscript boilerplate      │
│  Use abbreviations & symbolic shorthand     │
├─────────────────────────────────────────────┤
│  Layer 2: STRUCTURAL COMPRESSION            │
│  Force structured output (JSON/YAML/TOON)   │
│  Use tables, bullets, arrows over prose     │
│  Flatten nested explanations                │
│  Index mapping for classifiers              │
│  YAML over JSON where possible (15-30%)     │
├─────────────────────────────────────────────┤
│  Layer 3: SEMANTIC COMPRESSION              │
│  Omit obvious/inferable information         │
│  Merge redundant concepts                   │
│  Use domain-specific shorthand              │
│  Chain of Draft for reasoning (≤5 words/    │
│    step instead of verbose CoT)             │
└─────────────────────────────────────────────┘
```

Each layer compounds. L1 prompt applies Layer 1. L2 adds Layer 2. L3 applies all three.

---

## Adaptive Mode Detection (Recommended)

Blind compression across all tasks degrades reasoning quality. Research shows that
format restrictions cause measurable accuracy drops on reasoning tasks
(Tam et al., EMNLP 2024 — "Let Me Speak Freely?").

**The solution: detect the task type and compress selectively.**

| Signal | Mode | Compression |
|:-------|:-----|:------------|
| Imperative verb + code/file ("fix", "refactor", "add") | **Action** | L2 or L3 |
| Question word ("what", "why", "how", "should I") | **Reasoning** | L1 only |
| "Write me a", "Draft", "Create a doc/report" | **Creative** | None (full prose) |
| Tool run, result obvious | **Action** | L3 — stop after result |
| Debugging but user doesn't understand why | **Reasoning** | L1 |
| Short command, clear scope | **Action** | L2 or L3 |
| User message is terse and technical | **Mirror** | Match user's register |
| User message is casual and chatty | **Mirror** | Match user's register |

**Key principle**: Compress the *delivery format*, not the *thinking*.
Let the model reason freely (especially on reasoning models), then compress
only the final output. Never ask the model to "think like a caveman" — only
ask it to *communicate* concisely.

See [references/adaptive_modes.md](references/adaptive_modes.md) for the full
adaptive mode system prompt.

---

## Implementation Steps

### Step 1: Select compression level based on use case

Ask user (or infer from context):
- Is output **human-facing** or **machine-consumed**?
- Is it a **one-off** query or **batch/pipeline**?
- Is **readability** or **cost** the priority?

Decision matrix:
- Human-facing + readability priority → **L1 (Trim)**
- Developer workflow + balanced → **L2 (Compress)**
- Machine-consumed OR cost-critical → **L3 (Crush)**

### Step 2: Load the appropriate system prompt

Read the prompt file for the chosen level:
- L1: [prompts/L1_trim.md](prompts/L1_trim.md)
- L2: [prompts/L2_compress.md](prompts/L2_compress.md)
- L3: [prompts/L3_crush.md](prompts/L3_crush.md)

### Step 3: Apply per-model tuning (optional but recommended)

Different models respond to compression instructions differently. Read:
- [tuning/model_specific.md](tuning/model_specific.md)

### Step 4: Add structural optimization if needed

For additional savings beyond linguistic compression:
- [references/structural_optimization.md](references/structural_optimization.md)

### Step 5: Combine and deliver

Assemble the final system prompt by combining:
1. The compression-level prompt (Step 2)
2. Any model-specific overrides (Step 3)
3. Any structural directives (Step 4)
4. The user's original task/system instructions

**Order matters.** Place compression instructions **before** the task instructions
so the model internalizes the style constraints first.

---

## Important Caveats & Research Warnings

> **Format Restrictions Degrade Reasoning** (Tam et al., EMNLP 2024):
> Peer-reviewed research shows that structured format constraints cause
> "significant decline in LLMs' reasoning abilities" and that "stricter format
> constraints generally lead to greater performance degradation in reasoning tasks."
> This is why Token Thrift uses adaptive mode detection — never apply L3 to
> tasks requiring deep reasoning. Use L1 for reasoning, L2/L3 only for action tasks.
>
> Paper: https://aclanthology.org/2024.emnlp-industry.91/

> **Persona Trap**: Forcing a model to "talk like a caveman" or adopt a low-IQ
> persona doesn't just change the output style — it can shift the model's entire
> reasoning distribution toward lower-quality outputs. Token Thrift avoids this
> by constraining *format*, not *persona*. The prompts say "be concise" not
> "be dumb".

> **Thinking Budget**: On reasoning models (o1, o3, Claude with extended thinking),
> aggressive compression may cause the model to "spend" saved output tokens on
> internal reasoning about *how* to compress, potentially negating savings.
> For reasoning models, prefer L1 or use Chain of Draft (see L3 prompt).

> **Consistency Drift**: All models drift toward verbosity over long conversations.
> Re-inject a brief compression reminder every 5-10 turns. Example:
> `[Reminder: maintain compressed output style per initial instructions]`

> **Output ≠ Total Cost**: Compression only reduces output tokens. The dominant
> cost in most workflows is input context (chat history, files, system prompt)
> that gets re-read every turn. For total cost reduction, combine Token Thrift
> with input-side strategies (context caching, RAG optimization, conversation
> summarization). See [references/structural_optimization.md](references/structural_optimization.md).

---

## Measuring Results

To verify savings, compare token counts with and without compression:
1. Use the provider's usage API (`usage.completion_tokens` in OpenAI, etc.)
2. Or use the tokenizer estimation script: [scripts/estimate_tokens.py](scripts/estimate_tokens.py)

Track your savings over time with the logging template:
[references/token_tracking_template.md](references/token_tracking_template.md)
