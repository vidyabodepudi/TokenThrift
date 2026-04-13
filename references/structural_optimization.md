# Structural Optimization Guide

Beyond linguistic compression (how words are chosen), structural optimization
changes *what format* the output takes. These techniques compound with L1/L2/L3
prompts for maximum token savings.

---

## 1. Structured Output Formats

### JSON Mode (All Major Providers)

Force the model to output raw JSON instead of conversational prose.

| Provider | API Parameter |
|:---------|:-------------|
| OpenAI | `response_format: { type: "json_object" }` |
| Anthropic | Use Tool Use / function calling |
| Google Gemini | `response_mime_type: "application/json"` + `response_schema` |
| DeepSeek | `response_format: { type: "json_object" }` |

**Savings**: Eliminates ALL conversational overhead. Output contains only data.

### Schema Minimization

Even within JSON, you can compress:

```
BAD (verbose keys):
{
  "user_full_name": "Alice",
  "user_email_address": "alice@x.com",
  "account_creation_date": "2024-01-15",
  "is_premium_subscriber": true
}

GOOD (compact keys):
{
  "name": "Alice",
  "email": "alice@x.com",
  "created": "2024-01-15",
  "premium": true
}
```

Rules:
- Use shortest unambiguous key names
- Flatten nested objects when depth > 2
- Use `0`/`1` instead of `false`/`true` for bulk data
- Omit null/empty fields entirely

### TOON (Token-Oriented Object Notation)

For uniform arrays (lists of objects with same fields), TOON is 30-60% more
efficient than JSON:

```
JSON (expensive):
[
  {"name": "Alice", "age": 30, "role": "eng"},
  {"name": "Bob", "age": 25, "role": "pm"},
  {"name": "Carol", "age": 28, "role": "design"}
]

TOON (compact):
[3]{name,age,role}
Alice,30,eng
Bob,25,pm
Carol,28,design
```

**Best for**: Tabular data, search results, batch outputs.
**Avoid for**: Deeply nested or non-uniform data.

---

## 2. Output Structure Patterns

### Tables Over Lists

When comparing 2+ items across multiple dimensions, tables are more
token-efficient than prose or nested bullets:

```
VERBOSE (~45 tokens):
- Python: Interpreted, dynamically typed, great for scripting
- Rust: Compiled, statically typed, great for performance
- Go: Compiled, statically typed, great for concurrency

COMPACT TABLE (~30 tokens):
| Lang | Type | Typed | Strength |
|------|------|-------|----------|
| Python | Interp | Dynamic | Scripting |
| Rust | Compiled | Static | Perf |
| Go | Compiled | Static | Concurrency |
```

### Arrows for Causality

Replace "because", "therefore", "which leads to", "as a result":

```
VERBOSE: "The server ran out of memory because the cache was not bounded,
which caused the process to be killed by the OOM killer, and therefore
the service went down."

COMPRESSED: Unbounded cache → OOM → process killed → service down
```

### Diff Format for Changes

When describing modifications, use diff notation:

```
VERBOSE: "Change the timeout from 30 seconds to 60 seconds in the
configuration file, and also add a retry count of 3."

COMPRESSED:
- timeout: 30
+ timeout: 60
+ retries: 3
```

---

## 3. Response Templates

Pre-define output templates for common query types to eliminate format
negotiation tokens:

### Bug Report Template
```
**Bug**: [one-line description]
**Cause**: [root cause]
**Fix**: [solution]
**Prevent**: [optional — how to avoid recurrence]
```

### Code Review Template
```
**File**: `path`
**L[N]**: [issue] → [fix]
**L[N]**: [issue] → [fix]
```

### Decision Template
```
**Recommend**: [choice]
**Why**: [1-2 reasons]
**Risk**: [main risk]
**Alt**: [alternative if rejected]
```

---

## 4. Stop Sequences

Hard-stop the model before it generates wasteful content:

```python
# OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    stop=["\n\nIs there", "\n\nLet me know", "\n\nI hope", "\n\nFeel free"]
)

# Anthropic
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[...],
    stop_sequences=["Is there anything", "Let me know", "I hope this"]
)
```

This catches the model starting its postscript and cuts it off.

---

## 5. max_tokens Calibration

Set appropriate limits by response type:

| Response Type | Recommended max_tokens |
|:-------------|:----------------------|
| Classification/label | 5-10 |
| Yes/no + reason | 20-50 |
| Short answer | 50-150 |
| Code snippet | 100-300 |
| Explanation | 200-500 |
| Full code file | 500-2000 |
| Essay/analysis | 1000-4000 |

Set these explicitly in every API call. Never leave it unbounded.

---

## 6. Combining Everything

Maximum compression stack for a code Q&A pipeline:

```python
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    max_tokens=300,
    frequency_penalty=0.3,
    stop=["\n\nIs there", "\n\nLet me know"],
    messages=[
        {
            "role": "system",
            "content": L3_CRUSH_PROMPT + "\nOutput JSON: {answer: str, code: str}"
        },
        {
            "role": "user",
            "content": user_question
        }
    ]
)
```

This combines:
- L3 linguistic compression (prompt)
- JSON structural compression (response_format)
- Hard output cap (max_tokens)
- Repetition reduction (frequency_penalty)
- Postscript prevention (stop sequences)

Expected savings: **70-80%** vs. unoptimized baseline.
