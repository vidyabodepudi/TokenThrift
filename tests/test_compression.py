#!/usr/bin/env python3
"""
Token Thrift — Compression Level Test Suite

Demonstrates token savings across L1/L2/L3 by comparing real-world
"standard verbose" LLM responses against compressed equivalents.

Token estimation uses the ~4 characters/token heuristic (widely used
in the industry). For exact counts, install tiktoken separately.

Usage:
    python3 tests/test_compression.py
"""

import sys
import re

# ─────────────────────────────────────────────────────────────────
# Token estimation (no external dependencies)
# ─────────────────────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """
    Estimate token count using a hybrid heuristic:
    - Split on whitespace and punctuation boundaries
    - Apply the ~1.3 tokens per word rule (accounts for subword tokenization)
    This closely approximates cl100k_base for English text.
    """
    # Count "words" (sequences of alphanumeric + common programming chars)
    words = re.findall(r"[a-zA-Z0-9_]+|[^\s]", text)
    # Rough approximation: most English words are 1-2 tokens,
    # code tokens tend to be 1:1, punctuation is 1 token each
    # We use character-based estimation as a cross-check
    char_estimate = len(text) / 3.8  # ~3.8 chars per token for mixed content
    word_estimate = len(words) * 1.1  # ~1.1 tokens per word/symbol
    # Average the two methods for better accuracy
    return max(1, int((char_estimate + word_estimate) / 2))


# ─────────────────────────────────────────────────────────────────
# Test cases: (question, standard_response, L1, L2, L3)
# ─────────────────────────────────────────────────────────────────

TESTS = [
    {
        "name": "Simple factual question",
        "question": "What port does PostgreSQL use by default?",
        "standard": """Great question! PostgreSQL, which is one of the most popular open-source relational database management systems, uses port 5432 by default. This is the standard port that PostgreSQL listens on for incoming connections.

When you install PostgreSQL, it will automatically configure itself to listen on port 5432 unless you specify a different port during the installation process. You can change this setting in the postgresql.conf configuration file if needed.

It's worth noting that if you're running multiple PostgreSQL instances on the same machine, you'll need to configure each instance to use a different port to avoid conflicts.

Let me know if you have any other questions about PostgreSQL configuration!""",

        "L1": """PostgreSQL uses port 5432 by default.

Configurable in `postgresql.conf`. Multiple instances on same machine need different ports.""",

        "L2": """Port `5432`. Configurable in `postgresql.conf`.""",

        "L3": """`5432`""",
    },
    {
        "name": "How-to / tutorial",
        "question": "How do I reverse a string in Python?",
        "standard": """Sure! I'd be happy to help you with that. There are several ways to reverse a string in Python. Let me walk you through the most common approaches:

**Method 1: Using string slicing**
This is the most Pythonic and concise way to reverse a string:

```python
text = "Hello, World!"
reversed_text = text[::-1]
print(reversed_text)  # Output: !dlroW ,olleH
```

The `[::-1]` slice notation means "start at the end, go to the beginning, stepping backwards by 1."

**Method 2: Using the reversed() function**
You can also use Python's built-in `reversed()` function along with `join()`:

```python
text = "Hello, World!"
reversed_text = ''.join(reversed(text))
print(reversed_text)  # Output: !dlroW ,olleH
```

**Method 3: Using a loop**
If you want to understand the process step by step, you can use a loop:

```python
text = "Hello, World!"
reversed_text = ""
for char in text:
    reversed_text = char + reversed_text
print(reversed_text)  # Output: !dlroW ,olleH
```

Each of these methods has its own advantages. The slicing method is the fastest and most idiomatic in Python. The `reversed()` method is more readable if you're not familiar with slicing syntax. The loop method is the most verbose but helps you understand the underlying process.

I hope this helps! Let me know if you have any questions about these approaches.""",

        "L1": """**Slicing** (most common):
```python
text[::-1]
```

**`reversed()` + join**:
```python
''.join(reversed(text))
```

**Loop** (manual):
```python
reversed_text = ""
for char in text:
    reversed_text = char + reversed_text
```

Slicing is fastest and most idiomatic.""",

        "L2": """3 ways:

```python
# 1. Slicing (fastest, idiomatic)
text[::-1]

# 2. reversed() + join
''.join(reversed(text))

# 3. Loop
r = ""
for c in text:
    r = c + r
```""",

        "L3": """```python
text[::-1]
```""",
    },
    {
        "name": "Debug / error fix",
        "question": "ModuleNotFoundError: No module named 'requests'",
        "standard": """I see you're encountering a `ModuleNotFoundError` for the `requests` module. This error occurs because the `requests` library is not installed in your current Python environment.

The `requests` library is a popular third-party HTTP library for Python that isn't included in the standard library, so you need to install it separately.

Here's how you can fix this:

**Step 1: Install the requests library**
Open your terminal or command prompt and run:

```bash
pip install requests
```

If you're using Python 3 and have both Python 2 and Python 3 installed, you might need to use:

```bash
pip3 install requests
```

**Step 2: If you're using a virtual environment**
Make sure you've activated your virtual environment before installing:

```bash
# On macOS/Linux
source venv/bin/activate
pip install requests

# On Windows
venv\\Scripts\\activate
pip install requests
```

**Step 3: Verify the installation**
After installation, you can verify it's installed correctly by running:

```python
import requests
print(requests.__version__)
```

If you're still having issues, it might be because you have multiple Python installations and `pip` is installing the package for a different version than the one you're running your script with. In that case, try:

```bash
python -m pip install requests
```

This ensures you're installing the package for the correct Python interpreter.

Let me know if you're still experiencing any issues!""",

        "L1": """The `requests` library isn't installed in your current Python environment.

**Fix:**
```bash
pip install requests
```

If using a virtual environment, activate it first:
```bash
source venv/bin/activate
pip install requests
```

If multiple Python versions exist:
```bash
python -m pip install requests
```""",

        "L2": """Not installed in current env.

Fix:
```bash
pip install requests
```

If venv: activate first. If multi-python: `python -m pip install requests`.""",

        "L3": """`pip install requests`""",
    },
    {
        "name": "Comparison question",
        "question": "What's the difference between a list and a tuple in Python?",
        "standard": """That's a great question! Lists and tuples are both sequence data types in Python that can store collections of items, but they have some important differences. Let me explain them:

**1. Mutability**
- **Lists** are mutable, meaning you can change their contents after creation (add, remove, or modify elements).
- **Tuples** are immutable, meaning once they are created, you cannot change their contents.

```python
# List - mutable
my_list = [1, 2, 3]
my_list[0] = 10  # This works fine

# Tuple - immutable
my_tuple = (1, 2, 3)
my_tuple[0] = 10  # This raises a TypeError
```

**2. Syntax**
- Lists use square brackets: `[1, 2, 3]`
- Tuples use parentheses: `(1, 2, 3)`

**3. Performance**
- Tuples are generally faster than lists because of their immutability. Python can optimize memory allocation for tuples since it knows they won't change.
- Tuples also use less memory than lists.

**4. Use Cases**
- **Lists** are best when you need a collection that will change over time (adding/removing items, sorting, etc.)
- **Tuples** are best for fixed collections of related items (like coordinates, RGB colors, database records)

**5. Hashability**
- Tuples can be used as dictionary keys and in sets (because they're hashable)
- Lists cannot be used as dictionary keys (because they're not hashable)

**6. Built-in Methods**
- Lists have many built-in methods: `append()`, `extend()`, `insert()`, `remove()`, `pop()`, `sort()`, etc.
- Tuples only have two: `count()` and `index()`

In summary, use lists when you need a mutable, dynamic collection, and use tuples when you want an immutable, fixed collection that can also serve as a dictionary key.

I hope this clears things up! Feel free to ask if you have more questions.""",

        "L1": """| Aspect | List | Tuple |
|:-------|:-----|:------|
| Mutability | Mutable | Immutable |
| Syntax | `[1, 2, 3]` | `(1, 2, 3)` |
| Performance | Slower, more memory | Faster, less memory |
| Use case | Dynamic collections | Fixed/related data |
| Hashable | No (can't be dict key) | Yes (can be dict key) |
| Methods | Many (`append`, `sort`, etc.) | Two (`count`, `index`) |

Use lists for changing collections, tuples for fixed data or dict keys.""",

        "L2": """| | List | Tuple |
|---|---|---|
| Mutable | yes | no |
| Syntax | `[]` | `()` |
| Speed | Slower | Faster |
| Memory | More | Less |
| Dict key | no | yes |
| Methods | Many | 2 (`count`, `index`) |

List = dynamic data. Tuple = fixed data / dict keys.""",

        "L3": """| | List | Tuple |
|---|---|---|
| Mut | yes | no |
| Syn | `[]` | `()` |
| Perf | down | up |
| Key | no | yes |""",
    },
    {
        "name": "Code generation",
        "question": "Write a function to check if a number is prime",
        "standard": """Sure! Here's a Python function that checks whether a given number is prime:

```python
def is_prime(n):
    \"\"\"
    Check if a number is prime.
    
    A prime number is a natural number greater than 1 that has no positive 
    divisors other than 1 and itself.
    
    Args:
        n (int): The number to check.
    
    Returns:
        bool: True if the number is prime, False otherwise.
    \"\"\"
    # Handle edge cases
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    # Check for factors up to the square root of n
    # We only need to check numbers of the form 6k +/- 1
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    
    return True
```

Let me explain how this works:

1. **Edge cases**: Numbers less than or equal to 1 are not prime. Numbers 2 and 3 are prime.
2. **Even and divisible by 3**: We quickly eliminate numbers divisible by 2 or 3.
3. **6k +/- 1 optimization**: All primes greater than 3 are of the form 6k +/- 1. So we only check divisors of that form, starting from 5.
4. **Square root limit**: We only need to check up to the square root of n because if n has a factor larger than its square root, the corresponding factor would be smaller than the square root.

Here's how to use it:

```python
print(is_prime(2))   # True
print(is_prime(17))  # True
print(is_prime(4))   # False
print(is_prime(1))   # False
```

This function has a time complexity of O(sqrt(n)), which is quite efficient for most practical purposes. Let me know if you need any modifications!""",

        "L1": """```python
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
```

Uses 6k+/-1 optimization, only checks divisors up to sqrt(n). Time complexity: O(sqrt(n)).""",

        "L2": """```python
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True
```

O(sqrt(n)), checks 6k+/-1 divisors only.""",

        "L3": """```python
def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    i=5
    while i*i<=n:
        if n%i==0 or n%(i+2)==0: return False
        i+=6
    return True
```""",
    },
    {
        "name": "Architecture / reasoning question",
        "question": "Should I use Redis or Memcached for caching?",
        "standard": """That's a really good question, and the answer depends on your specific use case! Both Redis and Memcached are excellent in-memory caching solutions, but they have different strengths and capabilities. Let me break down the comparison for you:

**Redis** is more than just a cache. It is a full-featured in-memory data structure store. Here are its key advantages:

1. **Rich data structures**: Redis supports strings, hashes, lists, sets, sorted sets, streams, and more. This makes it incredibly versatile for various use cases beyond simple key-value caching.

2. **Persistence**: Redis can persist data to disk, which means your cache survives restarts. This is crucial for applications where cache warm-up time is expensive.

3. **Replication and clustering**: Redis has built-in support for master-slave replication and Redis Cluster for horizontal scaling.

4. **Pub/Sub**: Redis includes a publish/subscribe messaging system, which is useful for real-time applications.

5. **Lua scripting**: You can run Lua scripts directly on the Redis server, enabling complex atomic operations.

6. **TTL on keys**: Redis supports time-to-live on individual keys for automatic expiration.

**Memcached**, on the other hand, is a simpler, more focused caching solution:

1. **Simplicity**: Memcached is designed to do one thing well, which is to cache key-value pairs in memory. This simplicity makes it easy to set up and maintain.

2. **Multi-threaded**: Memcached is multi-threaded, which means it can take better advantage of multi-core systems for handling many concurrent connections.

3. **Memory efficiency**: For simple key-value string caching, Memcached can be more memory-efficient because it does not have the overhead of Redis's richer data structures.

4. **Horizontal scaling**: Memcached uses a simple distributed architecture where clients handle the distribution of keys across servers.

**When to choose Redis:**
- You need data structures beyond simple strings
- You need persistence (data survives restarts)
- You need pub/sub or real-time features
- You are using it as a primary data store, not just a cache
- You need atomic operations with Lua scripting

**When to choose Memcached:**
- You only need simple key-value string caching
- You want maximum simplicity in setup and maintenance
- You need to handle a very high number of concurrent connections
- Memory efficiency for simple caching is your top priority

**My recommendation**: In most modern applications, **Redis** is the better default choice because of its versatility, active development, and rich ecosystem. Memcached is still a solid choice if you specifically need a simple, lightweight, multi-threaded cache and do not need any of Redis's additional features.

Hope this helps you make your decision! Let me know if you would like more specific guidance based on your use case.""",

        "L1": """**Redis** in most cases. It does everything Memcached does plus:
- Rich data structures (hashes, lists, sets, sorted sets)
- Persistence (survives restarts)
- Pub/Sub messaging
- Replication and clustering built-in
- Lua scripting for atomic operations

**Memcached** only if you specifically need:
- Maximum simplicity (pure key-value string cache)
- Multi-threaded connection handling at extreme scale
- Slightly better memory efficiency for simple string caching

Redis is the better default for modern applications.""",

        "L2": """**Redis** (default choice):
- Rich data types (hash, list, set, sorted set)
- Persistence, survives restarts
- Pub/sub, Lua scripting, clustering
- More versatile, actively developed

**Memcached** only if:
- Pure string k/v cache needed
- Multi-threaded conn handling at scale
- Max simplicity priority

Redis > Memcached for most use cases.""",

        "L3": """Redis. Unless pure string k/v + max simplicity needed, then Memcached.

| | Redis | Memcached |
|---|---|---|
| Types | Many | str only |
| Persist | yes | no |
| Pub/sub | yes | no |
| Thread | Single | Multi |
| Complex | up | down |""",
    },
]


# ─────────────────────────────────────────────────────────────────
# Cost models (per 1M output tokens, USD)
# ─────────────────────────────────────────────────────────────────

PRICING = {
    "GPT-4o":           15.00,
    "GPT-4.1":           8.00,
    "Claude Sonnet 4":  15.00,
    "Claude Haiku":      5.00,
    "Gemini 2.5 Pro":   10.00,
    "Gemini 2.5 Flash":  2.50,
    "DeepSeek-V3":       1.10,
}


def main():
    print()
    print("=" * 78)
    print("  TOKEN THRIFT  —  Compression Test Suite")
    print("=" * 78)
    print()

    total_std = 0
    total_l1 = 0
    total_l2 = 0
    total_l3 = 0

    for i, test in enumerate(TESTS, 1):
        std_tok = estimate_tokens(test["standard"])
        l1_tok = estimate_tokens(test["L1"])
        l2_tok = estimate_tokens(test["L2"])
        l3_tok = estimate_tokens(test["L3"])

        total_std += std_tok
        total_l1 += l1_tok
        total_l2 += l2_tok
        total_l3 += l3_tok

        l1_pct = (1 - l1_tok / std_tok) * 100
        l2_pct = (1 - l2_tok / std_tok) * 100
        l3_pct = (1 - l3_tok / std_tok) * 100

        preview_std = test["standard"][:55].replace("\n", " ").strip()
        preview_l1 = test["L1"][:55].replace("\n", " ").strip()
        preview_l2 = test["L2"][:55].replace("\n", " ").strip()
        preview_l3 = test["L3"][:55].replace("\n", " ").strip()

        print(f"  Test {i}: {test['name']}")
        print(f"  Q: \"{test['question']}\"")
        print(f"  {'─' * 72}")
        print(f"  {'Level':<14} {'Tokens':>8} {'Saved':>8}  Preview")
        print(f"  {'─' * 72}")
        print(f"  {'Standard':<14} {std_tok:>8} {'—':>8}  {preview_std}...")
        print(f"  {'L1 Trim':<14} {l1_tok:>8} {l1_pct:>7.1f}%  {preview_l1}...")
        print(f"  {'L2 Compress':<14} {l2_tok:>8} {l2_pct:>7.1f}%  {preview_l2}...")
        print(f"  {'L3 Crush':<14} {l3_tok:>8} {l3_pct:>7.1f}%  {preview_l3}...")
        print()

    # ─── Aggregate Summary ───
    print("=" * 78)
    print("  AGGREGATE RESULTS")
    print("=" * 78)
    print()

    l1_total_pct = (1 - total_l1 / total_std) * 100
    l2_total_pct = (1 - total_l2 / total_std) * 100
    l3_total_pct = (1 - total_l3 / total_std) * 100

    print(f"  {'Level':<16} {'Total Tokens':>14} {'vs Standard':>14} {'Savings':>10}")
    print(f"  {'─' * 56}")
    print(f"  {'Standard':<16} {total_std:>14,} {'—':>14} {'—':>10}")
    print(f"  {'L1 Trim':<16} {total_l1:>14,} {total_l1 - total_std:>+14,} {l1_total_pct:>9.1f}%")
    print(f"  {'L2 Compress':<16} {total_l2:>14,} {total_l2 - total_std:>+14,} {l2_total_pct:>9.1f}%")
    print(f"  {'L3 Crush':<16} {total_l3:>14,} {total_l3 - total_std:>+14,} {l3_total_pct:>9.1f}%")
    print()

    # ─── Cost Projections ───
    print("=" * 78)
    print("  COST PROJECTIONS  (per 10,000 requests at this token mix)")
    print("=" * 78)
    print()

    scale = 10_000
    print(f"  {'Model':<20} {'Standard':>10} {'L1 Trim':>10} {'L2 Comp':>10} {'L3 Crush':>10}")
    print(f"  {'─' * 62}")
    for model, price in PRICING.items():
        cost_std = (total_std / 1_000_000) * price * scale
        cost_l1 =  (total_l1 / 1_000_000) * price * scale
        cost_l2 =  (total_l2 / 1_000_000) * price * scale
        cost_l3 =  (total_l3 / 1_000_000) * price * scale
        print(f"  {model:<20} ${cost_std:>8.2f} ${cost_l1:>8.2f} ${cost_l2:>8.2f} ${cost_l3:>8.2f}")

    print()
    print(f"  Note: Output token costs only. Input costs unchanged.")
    print(f"  Based on {len(TESTS)} task types x {scale:,} requests each.")
    print()

    # ─── Visual Bar Chart ───
    print("=" * 78)
    print("  TOKEN REDUCTION  (visual)")
    print("=" * 78)
    print()

    BAR_WIDTH = 35
    for test in TESTS:
        std_tok = estimate_tokens(test["standard"])
        l1_tok = estimate_tokens(test["L1"])
        l2_tok = estimate_tokens(test["L2"])
        l3_tok = estimate_tokens(test["L3"])

        print(f"  {test['name']}")
        for label, tok in [("Std", std_tok), ("L1 ", l1_tok), ("L2 ", l2_tok), ("L3 ", l3_tok)]:
            ratio = tok / std_tok
            bar_len = max(1, int(ratio * BAR_WIDTH))
            bar = "\u2588" * bar_len + "\u2591" * (BAR_WIDTH - bar_len)
            if label == "Std":
                print(f"    {label} {bar} {tok:>4} tok")
            else:
                pct = (1 - ratio) * 100
                print(f"    {label} {bar} {tok:>4} tok  (-{pct:.0f}%)")
        print()

    # ─── Summary ───
    print("=" * 78)
    print(f"  SUMMARY")
    print(f"  " + "─" * 40)
    print(f"  L1 Trim:      {l1_total_pct:.1f}% avg reduction  (safe for all tasks)")
    print(f"  L2 Compress:  {l2_total_pct:.1f}% avg reduction  (great for dev workflows)")
    print(f"  L3 Crush:     {l3_total_pct:.1f}% avg reduction  (action tasks only)")
    print(f"")
    print(f"  Copy prompts from prompts/L1_trim.md, L2_compress.md, or L3_crush.md")
    print(f"  and paste into your LLM's system message to apply.")
    print("=" * 78)
    print()


if __name__ == "__main__":
    main()
