#!/usr/bin/env python3
"""
Token Thrift — Live API Test

Sends identical questions to Gemini with and without compression prompts,
measures actual token counts from the API response, and compares results.

Usage:
    GEMINI_API_KEY=your_key python3 tests/test_live.py
"""

import os
import sys
import time
import tiktoken

from google import genai

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-2.5-flash"

# Compression system prompts
SYSTEM_PROMPTS = {
    "Standard": "You are a helpful assistant.",

    "L1 Trim": """RESPONSE STYLE RULES — follow strictly:

1. NO preamble. Never start with "I'd be happy to help", "Sure!", "Great question",
   "Certainly", or similar filler. Begin directly with the answer.
2. NO postscript. Never end with "Let me know if you need anything else",
   "Hope this helps!", or similar sign-offs.
3. NO hedging filler. Avoid "It's worth noting that", "It's important to remember",
   "As you may know", "Interestingly enough". State facts directly.
4. NO restating the question. Do not echo back what the user asked.
5. NO unnecessary transitions. Drop "Furthermore", "Additionally", "Moreover",
   "In addition to that" when a simple line break or bullet suffices.
6. PREFER bullet points over paragraphs for lists of 3+ items.
7. PREFER code/examples over explanations when the user is technical.
8. ONE explanation per concept. Do not rephrase the same idea multiple ways
   "for clarity".
9. Use ACTIVE voice. "X does Y" not "Y is done by X".
10. Omit articles (a, an, the) where meaning is preserved.

These rules override all default verbosity preferences. Maintain full technical
accuracy and completeness — only remove stylistic waste.""",

    "L2 Compress": """RESPONSE COMPRESSION PROTOCOL — strict compliance required:

ELIMINATE:
- All preamble/postscript ("Happy to help", "Let me know", etc.)
- All hedging ("It's worth noting", "It should be mentioned")
- All question restating
- Articles (a/an/the) where meaning survives
- Filler transitions (Additionally/Furthermore/Moreover)
- Redundant explanations — say it once

FORMAT RULES:
- Bullets > paragraphs. Always.
- Tables > lists when comparing 2+ items
- Use arrows (→) for cause/effect and transformations
- Use shorthand: fn, var, arg, param, config, init, db, auth, req, res, impl,
  dep, pkg, env, repo, dir, cmd, err, msg, val, obj, arr, str, int, bool,
  async, sync, cb, ctx, ref, spec, util, lib, mod, src, dist, dev, prod,
  stmt, expr, decl, def, ret, iter
- Inline code for all: file names, commands, variables, values, paths
- Max 1 sentence lead-in per section, then bullets
- For classifications/labels: return index numbers, not full text
- Prefer YAML over JSON for structured output (15-30% fewer tokens)

STRUCTURE:
- Answer first, context second
- Lead with the solution, follow with the "why" only if non-obvious
- Group related items, don't scatter
- Flatten nested explanations — prefer a single level of bullets

BREVITY TARGETS:
- Simple factual question → 1-3 lines
- How-to/tutorial → numbered steps, no prose padding
- Code question → code block + ≤2 lines of annotation
- Comparison → table
- Debug/error → cause → fix → (optional) prevention""",

    "L3 Crush": """MAXIMUM TOKEN COMPRESSION — absolute minimum output:

STYLE:
- Telegraphic. No articles, no conjunctions, no filler.
- Drop pronouns when subject obvious from context.
- Use symbolic operators: → (leads to), = (equals/means), != (not),
  > (better than), < (worse than), ∴ (therefore), ∵ (because),
  ≈ (approximately), ✓ (yes/correct), ✗ (no/wrong), ↑ (increase),
  ↓ (decrease), ⚠ (warning), △ (change/delta)
- Max 5 words per bullet point where possible.
- Compress names: function→fn, variable→var, argument→arg,
  parameter→param, configuration→cfg, initialize→init,
  database→db, authenticate→auth, request→req, response→res,
  implement→impl, dependency→dep, package→pkg, environment→env,
  repository→repo, directory→dir, command→cmd, error→err,
  message→msg, value→val, object→obj, array→arr, string→str,
  integer→int, boolean→bool, callback→cb, context→ctx,
  reference→ref, specification→spec, utility→util, library→lib,
  module→mod, source→src, distribution→dist, development→dev,
  production→prod, statement→stmt, expression→expr,
  declaration→decl, definition→def, return→ret, iterator→iter,
  middleware→mw, controller→ctrl, service→svc, component→cmp

STRUCTURE:
- No section headers unless 3+ distinct topics
- Flat bullets only. No sub-bullets.
- Code blocks: strip all comments. Minimal variable names.
- Tables only for 3+ item comparisons
- One-line answers when possible
- Classifications/labels: return index number only (0, 1, 2...)
- Structured data: YAML not JSON (fewer syntax tokens)

REASONING (Chain of Draft):
- When showing reasoning steps, limit each step to ≤5 words
- Capture ONLY the minimal info needed to reach next step
- Like human scratch notes, not full sentences

OMIT:
- ALL preamble/postscript
- ALL hedging/caveats unless safety-critical
- ALL restating of question
- Explanations of obvious things
- "Why" unless explicitly asked
- Type annotations in examples unless relevant to question
- Import statements unless non-obvious
- Error handling in examples unless that's the topic

ANSWER FORMAT:
- Factual Q → direct val
- How-to → numbered steps, ≤5 words each
- Code Q → code block only, zero prose
- Debug → cause → fix (2 lines max)
- Compare → table, no prose
- Opinion → ranked list, no justification unless asked""",
}

# Test questions spanning different task types
TEST_QUESTIONS = [
    ("Factual", "What port does PostgreSQL use by default?"),
    ("How-to", "How do I reverse a string in Python?"),
    ("Debug", "I'm getting 'ModuleNotFoundError: No module named requests' in Python. How do I fix this?"),
    ("Comparison", "What's the difference between a list and a tuple in Python?"),
    ("Code Gen", "Write a Python function to check if a number is prime."),
    ("Architecture", "Should I use Redis or Memcached for caching in a web application?"),
]


def count_tokens_tiktoken(text: str) -> int:
    """Count tokens using tiktoken cl100k_base encoding."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def call_gemini(client, system_prompt: str, user_question: str, max_retries: int = 3) -> dict:
    """Call Gemini API with retry logic for rate limits."""
    start = time.time()

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_question,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.3,
                },
            )
            break
        except Exception as e:
            err_str = str(e)
            if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "503" in err_str) and attempt < max_retries - 1:
                wait = 20 * (attempt + 1)  # 20s, 40s, 60s
                print(f" [wait {wait}s]", end="", flush=True)
                time.sleep(wait)
            else:
                raise

    elapsed = time.time() - start
    text = response.text or ""

    # Get token counts from API response metadata
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else 0
    output_tokens = usage.candidates_token_count if usage else 0
    # Also count with tiktoken for cross-reference
    tiktoken_count = count_tokens_tiktoken(text)

    return {
        "text": text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tiktoken_count": tiktoken_count,
        "elapsed": elapsed,
    }


def main():
    if not API_KEY:
        print("ERROR: Set GEMINI_API_KEY environment variable")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    print()
    print("=" * 85)
    print("  TOKEN THRIFT — Live API Test")
    print(f"  Model: {MODEL}")
    print("=" * 85)
    print()

    # Collect all results
    results = {}
    for level_name, system_prompt in SYSTEM_PROMPTS.items():
        results[level_name] = []
        print(f"  Testing {level_name}...", end="", flush=True)
        for task_type, question in TEST_QUESTIONS:
            try:
                result = call_gemini(client, system_prompt, question)
                result["task"] = task_type
                result["question"] = question
                results[level_name].append(result)
                print(f" ✓", end="", flush=True)
            except Exception as e:
                print(f" ✗({e})", end="", flush=True)
                results[level_name].append({
                    "task": task_type,
                    "question": question,
                    "text": f"ERROR: {e}",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "tiktoken_count": 0,
                    "elapsed": 0,
                })
            time.sleep(13)  # Stay within 5 RPM free tier
        print()

    print()

    # ─── Per-Question Results ───
    print("=" * 85)
    print("  PER-QUESTION RESULTS (API-reported output tokens)")
    print("=" * 85)
    print()

    for i, (task_type, question) in enumerate(TEST_QUESTIONS):
        std_tokens = results["Standard"][i]["output_tokens"]
        print(f"  {task_type}: \"{question}\"")
        print(f"  {'─' * 78}")
        print(f"  {'Level':<16} {'Out Tokens':>12} {'Tiktoken':>10} {'Savings':>10} {'Time':>8}")
        print(f"  {'─' * 78}")

        for level_name in SYSTEM_PROMPTS:
            r = results[level_name][i]
            out_tok = r["output_tokens"]
            tik_tok = r["tiktoken_count"]
            elapsed = r["elapsed"]
            if level_name == "Standard":
                print(f"  {level_name:<16} {out_tok:>12} {tik_tok:>10} {'—':>10} {elapsed:>7.1f}s")
            else:
                savings = (1 - out_tok / std_tokens) * 100 if std_tokens > 0 else 0
                print(f"  {level_name:<16} {out_tok:>12} {tik_tok:>10} {savings:>9.1f}% {elapsed:>7.1f}s")
        print()

    # ─── Aggregate ───
    print("=" * 85)
    print("  AGGREGATE RESULTS")
    print("=" * 85)
    print()

    level_totals = {}
    for level_name in SYSTEM_PROMPTS:
        total_out = sum(r["output_tokens"] for r in results[level_name])
        total_tik = sum(r["tiktoken_count"] for r in results[level_name])
        total_time = sum(r["elapsed"] for r in results[level_name])
        level_totals[level_name] = (total_out, total_tik, total_time)

    std_total = level_totals["Standard"][0]
    print(f"  {'Level':<16} {'Total Out Tok':>14} {'Tiktoken':>10} {'Savings':>10} {'Total Time':>12}")
    print(f"  {'─' * 66}")
    for level_name, (total_out, total_tik, total_time) in level_totals.items():
        if level_name == "Standard":
            print(f"  {level_name:<16} {total_out:>14,} {total_tik:>10,} {'—':>10} {total_time:>11.1f}s")
        else:
            savings = (1 - total_out / std_total) * 100 if std_total > 0 else 0
            print(f"  {level_name:<16} {total_out:>14,} {total_tik:>10,} {savings:>9.1f}% {total_time:>11.1f}s")
    print()

    # ─── Cost Projections ───
    print("=" * 85)
    print("  COST PROJECTIONS (per 10,000 requests at this token mix)")
    print("=" * 85)
    print()

    PRICING = {
        "GPT-4o":           15.00,
        "GPT-4.1":           8.00,
        "Claude Sonnet 4":  15.00,
        "Claude Haiku":      5.00,
        "Gemini 2.5 Pro":   10.00,
        "Gemini 2.5 Flash":  2.50,
        "DeepSeek-V3":       1.10,
    }

    scale = 10_000
    print(f"  {'Model':<20} {'Standard':>10} {'L1 Trim':>10} {'L2 Comp':>10} {'L3 Crush':>10}")
    print(f"  {'─' * 62}")
    for model_name, price in PRICING.items():
        costs = []
        for level_name in SYSTEM_PROMPTS:
            total_out = level_totals[level_name][0]
            cost = (total_out / 1_000_000) * price * scale
            costs.append(cost)
        print(f"  {model_name:<20} ${costs[0]:>8.2f} ${costs[1]:>8.2f} ${costs[2]:>8.2f} ${costs[3]:>8.2f}")
    print()
    print(f"  Note: Output token costs only. Based on actual API output from {MODEL}.")
    print()

    # ─── Visual Comparison ───
    print("=" * 85)
    print("  TOKEN REDUCTION (visual, API-reported)")
    print("=" * 85)
    print()

    BAR_WIDTH = 40
    for i, (task_type, question) in enumerate(TEST_QUESTIONS):
        std_tok = results["Standard"][i]["output_tokens"]
        if std_tok == 0:
            continue
        print(f"  {task_type}")
        for level_name in SYSTEM_PROMPTS:
            tok = results[level_name][i]["output_tokens"]
            ratio = min(tok / std_tok, 1.0) if std_tok > 0 else 0
            bar_len = max(1, int(ratio * BAR_WIDTH))
            bar = "█" * bar_len + "░" * (BAR_WIDTH - bar_len)
            if level_name == "Standard":
                print(f"    {'Std':<6} {bar} {tok:>5}")
            else:
                short = level_name.split()[0]
                pct = (1 - ratio) * 100
                print(f"    {short:<6} {bar} {tok:>5}  (-{pct:.0f}%)")
        print()

    # ─── Sample Outputs ───
    print("=" * 85)
    print("  SAMPLE OUTPUTS (first question: PostgreSQL port)")
    print("=" * 85)
    print()

    for level_name in SYSTEM_PROMPTS:
        r = results[level_name][0]
        text = r["text"]
        print(f"  ── {level_name} ({r['output_tokens']} tokens) ──")
        # Indent and truncate long outputs
        lines = text.strip().split("\n")
        for line in lines[:15]:
            print(f"  │ {line}")
        if len(lines) > 15:
            print(f"  │ ... ({len(lines) - 15} more lines)")
        print()

    print("=" * 85)
    print("  Test complete!")
    print("=" * 85)
    print()


if __name__ == "__main__":
    main()
