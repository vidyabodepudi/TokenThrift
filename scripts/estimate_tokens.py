#!/usr/bin/env python3
"""
Token Thrift — Token Estimation & Comparison Script

Estimates token counts for text using tiktoken (OpenAI's tokenizer).
Use this to compare output before/after compression to measure savings.

Usage:
    python estimate_tokens.py "your text here"
    python estimate_tokens.py --file response.txt
    python estimate_tokens.py --compare before.txt after.txt
    python estimate_tokens.py --interactive
    echo "text" | python estimate_tokens.py --stdin

Requirements:
    pip install tiktoken
"""

import argparse
import sys

try:
    import tiktoken
except ImportError:
    print("ERROR: tiktoken not installed. Run: pip install tiktoken")
    sys.exit(1)


# Model-to-encoding mapping (approximate — different models use different tokenizers,
# but cl100k_base covers GPT-4/4o/Claude-approximation and o200k_base covers newer models)
ENCODINGS = {
    "gpt-4": "cl100k_base",
    "gpt-4o": "o200k_base",
    "gpt-4.1": "o200k_base",
    "claude": "cl100k_base",       # Approximate — Claude uses its own tokenizer
    "gemini": "cl100k_base",       # Approximate
    "default": "cl100k_base",
}


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using the specified encoding."""
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def estimate_cost(token_count: int, price_per_million: float = 15.0) -> float:
    """Estimate cost in USD. Default price is GPT-4o output ($15/1M tokens)."""
    return (token_count / 1_000_000) * price_per_million


def compare_texts(before: str, after: str, encoding_name: str = "cl100k_base"):
    """Compare token counts between before and after compression."""
    before_tokens = count_tokens(before, encoding_name)
    after_tokens = count_tokens(after, encoding_name)

    savings = before_tokens - after_tokens
    pct = (savings / before_tokens * 100) if before_tokens > 0 else 0

    print(f"{'Metric':<25} {'Before':>10} {'After':>10} {'Delta':>10}")
    print(f"{'-'*55}")
    print(f"{'Characters':<25} {len(before):>10} {len(after):>10} {len(after)-len(before):>+10}")
    print(f"{'Tokens':<25} {before_tokens:>10} {after_tokens:>10} {-savings:>+10}")
    print(f"{'Reduction':<25} {'':>10} {'':>10} {pct:>9.1f}%")
    print()

    # Cost estimates for common models
    models = [
        ("GPT-4o output", 15.0),
        ("GPT-4.1 output", 8.0),
        ("Claude Sonnet output", 15.0),
        ("Claude Haiku output", 5.0),
        ("Gemini 2.5 Pro output", 10.0),
        ("Gemini 2.5 Flash output", 2.50),
        ("DeepSeek-V3 output", 1.10),
    ]

    print(f"{'Model':<25} {'Before $/1K':>12} {'After $/1K':>12} {'Save $/1K':>12}")
    print(f"{'-'*61}")
    for model_name, price in models:
        cost_before = estimate_cost(before_tokens, price) * 1000
        cost_after = estimate_cost(after_tokens, price) * 1000
        cost_saved = cost_before - cost_after
        print(f"{model_name:<25} ${cost_before:>10.4f} ${cost_after:>10.4f} ${cost_saved:>10.4f}")


def interactive_mode(encoding_name: str = "cl100k_base"):
    """Interactive REPL for quick token counting."""
    print("Token Thrift — Interactive Mode")
    print("Type text to count tokens. Commands: /compare, /quit")
    print()

    while True:
        try:
            text = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if text == "/quit":
            break
        elif text == "/compare":
            print("Paste BEFORE text (end with empty line):")
            before_lines = []
            while True:
                line = input()
                if line == "":
                    break
                before_lines.append(line)
            print("Paste AFTER text (end with empty line):")
            after_lines = []
            while True:
                line = input()
                if line == "":
                    break
                after_lines.append(line)
            compare_texts("\n".join(before_lines), "\n".join(after_lines), encoding_name)
        elif text:
            tokens = count_tokens(text, encoding_name)
            print(f"  → {tokens} tokens ({len(text)} chars)")


def main():
    parser = argparse.ArgumentParser(
        description="Token Thrift — Estimate and compare token counts"
    )
    parser.add_argument("text", nargs="?", help="Text to count tokens for")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--compare", "-c", nargs=2, metavar=("BEFORE", "AFTER"),
                        help="Compare two files")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive REPL mode")
    parser.add_argument("--model", "-m", default="default",
                        choices=list(ENCODINGS.keys()),
                        help="Model to use for tokenization (default: cl100k_base)")

    args = parser.parse_args()
    encoding = ENCODINGS[args.model]

    if args.interactive:
        interactive_mode(encoding)
    elif args.compare:
        with open(args.compare[0]) as f:
            before = f.read()
        with open(args.compare[1]) as f:
            after = f.read()
        compare_texts(before, after, encoding)
    elif args.file:
        with open(args.file) as f:
            text = f.read()
        tokens = count_tokens(text, encoding)
        print(f"File: {args.file}")
        print(f"Tokens: {tokens}")
        print(f"Characters: {len(text)}")
    elif args.stdin:
        text = sys.stdin.read()
        tokens = count_tokens(text, encoding)
        print(f"Tokens: {tokens}")
    elif args.text:
        tokens = count_tokens(args.text, encoding)
        print(f"Tokens: {tokens}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
