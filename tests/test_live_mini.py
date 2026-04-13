#!/usr/bin/env python3
"""
Token Thrift — Minimal Live Test (Free Tier Safe)

Only 2 questions × 4 compression levels = 8 API calls.
Fits within Gemini free tier limits (20 RPD, 5 RPM).

Usage:
    GEMINI_API_KEY=your_key python3 tests/test_live_mini.py
"""

import os
import sys
import time
import tiktoken

from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-3-flash-preview"

enc = tiktoken.get_encoding("cl100k_base")

SYSTEM_PROMPTS = {
    "Standard": "You are a helpful assistant.",

    "L1 Trim": """RESPONSE STYLE RULES — follow strictly:
1. NO preamble ("Sure!", "Great question!", "I'd be happy to help").
2. NO postscript ("Let me know if you need anything").
3. NO hedging ("It's worth noting", "It's important to remember").
4. NO restating the question.
5. NO transitions ("Furthermore", "Additionally").
6. Bullets > paragraphs for 3+ items.
7. ONE explanation per concept. No rephrasing "for clarity".
8. Omit articles (a/an/the) where meaning is preserved.
Maintain full technical accuracy — only remove stylistic waste.""",

    "L2 Compress": """RESPONSE COMPRESSION — strict compliance:
ELIMINATE: preamble, postscript, hedging, question restating, articles, transitions, redundant explanations.
FORMAT: bullets always > paragraphs. Tables for comparisons. Arrows (→) for causality. Use shorthand: fn, var, arg, param, cfg, db, auth, req, res, impl, dep, pkg, env, repo, dir, cmd, err.
STRUCTURE: answer first, context second. Flatten explanations. Max 1 sentence lead-in then bullets.
TARGETS: factual→1-3 lines. How-to→numbered steps. Code→code block + ≤2 lines. Compare→table. Debug→cause→fix.""",

    "L3 Crush": """MAXIMUM TOKEN COMPRESSION:
STYLE: Telegraphic. No articles/conjunctions/filler. Drop pronouns. Max 5 words/bullet. Compress: function→fn, variable→var, parameter→param, database→db, environment→env, repository→repo, directory→dir, command→cmd, error→err.
Use: → (causality) ✓/✗ (yes/no) ↑/↓ (increase/decrease) ⚠ (warning).
STRUCTURE: flat bullets only. Code: strip comments, minimal names. One-line answers when possible.
OMIT: ALL preamble/postscript/hedging/restating. Explanations of obvious things. "Why" unless asked. Imports unless non-obvious.
FORMAT: Factual→direct val. How-to→steps ≤5 words each. Code→code block only. Debug→cause→fix 2 lines max. Compare→table no prose.""",
}

QUESTIONS = [
    ("How-to", "How do I reverse a string in Python?"),
    ("Architecture", "Should I use Redis or Memcached for caching?"),
]


def call_gemini(client, system_prompt, question, retries=3):
    for attempt in range(retries):
        try:
            start = time.time()
            resp = client.models.generate_content(
                model=MODEL,
                contents=question,
                config={"system_instruction": system_prompt, "temperature": 0.3},
            )
            elapsed = time.time() - start
            text = resp.text or ""
            usage = resp.usage_metadata
            return {
                "text": text,
                "api_out": usage.candidates_token_count if usage else 0,
                "api_in": usage.prompt_token_count if usage else 0,
                "tiktoken": len(enc.encode(text)),
                "elapsed": elapsed,
            }
        except Exception as e:
            if ("429" in str(e) or "503" in str(e)) and attempt < retries - 1:
                wait = 25 * (attempt + 1)
                print(f" [retry in {wait}s]", end="", flush=True)
                time.sleep(wait)
            else:
                raise
    return None


def main():
    if not API_KEY:
        print("ERROR: Set GEMINI_API_KEY"); sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    print()
    print("=" * 80)
    print(f"  TOKEN THRIFT — Live Mini Test  (model: {MODEL})")
    print("=" * 80)

    results = {}
    for level, sysprompt in SYSTEM_PROMPTS.items():
        results[level] = []
        print(f"\n  {level}:", end="", flush=True)
        for task, q in QUESTIONS:
            try:
                r = call_gemini(client, sysprompt, q)
                r["task"] = task
                results[level].append(r)
                print(f" ✓({r['api_out']}tok)", end="", flush=True)
            except Exception as e:
                print(f" ✗", end="", flush=True)
                results[level].append({"task": task, "text": str(e), "api_out": 0, "api_in": 0, "tiktoken": 0, "elapsed": 0})
            time.sleep(14)  # 5 RPM safe
    print("\n")

    # ═══ Per-question comparison ═══
    print("=" * 80)
    print("  RESULTS BY QUESTION")
    print("=" * 80)

    for qi, (task, q) in enumerate(QUESTIONS):
        std = results["Standard"][qi]["api_out"]
        print(f"\n  Q: \"{q}\"")
        print(f"  {'Level':<16} {'API Tokens':>12} {'Tiktoken':>10} {'Savings':>10} {'Time':>8}")
        print(f"  {'─' * 60}")
        for level in SYSTEM_PROMPTS:
            r = results[level][qi]
            out = r["api_out"]
            tik = r["tiktoken"]
            t = r["elapsed"]
            if level == "Standard" or std == 0:
                print(f"  {level:<16} {out:>12} {tik:>10} {'—':>10} {t:>7.1f}s")
            else:
                sav = (1 - out / std) * 100 if std > 0 else 0
                print(f"  {level:<16} {out:>12} {tik:>10} {sav:>9.1f}% {t:>7.1f}s")

    # ═══ Totals ═══
    print(f"\n{'=' * 80}")
    print("  AGGREGATE")
    print("=" * 80)
    print()

    std_total = sum(r["api_out"] for r in results["Standard"])
    print(f"  {'Level':<16} {'Total Tokens':>14} {'Savings':>10}")
    print(f"  {'─' * 42}")
    for level in SYSTEM_PROMPTS:
        total = sum(r["api_out"] for r in results[level])
        if level == "Standard":
            print(f"  {level:<16} {total:>14,} {'—':>10}")
        else:
            sav = (1 - total / std_total) * 100 if std_total > 0 else 0
            print(f"  {level:<16} {total:>14,} {sav:>9.1f}%")

    # ═══ Sample outputs ═══
    print(f"\n{'=' * 80}")
    print("  SAMPLE OUTPUTS — \"How do I reverse a string in Python?\"")
    print("=" * 80)

    for level in SYSTEM_PROMPTS:
        r = results[level][0]
        if r["api_out"] == 0:
            continue
        print(f"\n  ── {level} ({r['api_out']} API tokens, {r['tiktoken']} tiktoken) ──")
        lines = r["text"].strip().split("\n")
        for line in lines[:20]:
            print(f"  │ {line}")
        if len(lines) > 20:
            print(f"  │ ... ({len(lines) - 20} more lines)")

    # ═══ Cost table ═══
    print(f"\n{'=' * 80}")
    print("  COST PROJECTIONS (per 10,000 requests)")
    print("=" * 80)
    print()

    PRICING = {"GPT-4o": 15.0, "GPT-4.1": 8.0, "Claude Sonnet 4": 15.0,
               "Gemini 2.5 Pro": 10.0, "Gemini 2.5 Flash": 2.5, "DeepSeek-V3": 1.1}

    print(f"  {'Model':<20} {'Standard':>10} {'L1':>10} {'L2':>10} {'L3':>10}")
    print(f"  {'─' * 62}")
    for name, price in PRICING.items():
        costs = []
        for level in SYSTEM_PROMPTS:
            total = sum(r["api_out"] for r in results[level])
            costs.append((total / 1_000_000) * price * 10_000)
        print(f"  {name:<20} ${costs[0]:>8.2f} ${costs[1]:>8.2f} ${costs[2]:>8.2f} ${costs[3]:>8.2f}")

    print(f"\n{'=' * 80}")
    print(f"  Done! {sum(sum(1 for r in results[l] if r['api_out'] > 0) for l in SYSTEM_PROMPTS)}/8 calls succeeded.")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
