# Model-Specific Tuning Guide

Different LLMs have varying degrees of compliance with compression instructions.
This guide provides per-model overrides and tips to maximize token savings.

---

## OpenAI Models (GPT-4o, GPT-4.1, o1, o3, o4-mini)

### GPT-4o / GPT-4.1
- **Compliance**: Excellent. Follows compression rules consistently.
- **Tip**: Leverage `response_format: { type: "json_object" }` or Structured Outputs
  for machine-consumed responses — eliminates prose entirely.
- **Override**: Add `"max_tokens": N` in API call to hard-cap output length.
- **Bonus**: Use `frequency_penalty: 0.3` to reduce repetition → fewer wasted tokens.

### o1 / o3 / o4-mini (Reasoning Models)
- **Compliance**: Moderate. These models prioritize reasoning chain completeness.
- **⚠ Warning**: Aggressive compression (L3) can cause the model to "reason about
  how to compress" in its thinking tokens, potentially increasing total cost.
- **Recommendation**: Use L1 or L2 max. Don't fight the reasoning architecture.
- **Override**: Set `max_completion_tokens` instead of `max_tokens` for these models.

---

## Anthropic Models (Claude Opus 4, Claude Sonnet 4, Haiku)

### Claude Sonnet 4 / Opus 4
- **Compliance**: Very good, but Claude has strong RLHF tendencies toward helpfulness.
- **Tip**: Claude responds well to explicit "persona" instructions. Prefix compression
  prompt with: `You are a terse technical expert. You never use filler.`
- **Override**: Claude supports `stop_sequences` — add `["\n\nIs there", "\n\nLet me know",
  "\n\nFeel free"]` to cut postscript if it leaks through.
- **Bonus**: Use Tool Use / function calling for structured output — more reliable than
  asking Claude to output raw JSON in the response body.

### Claude with Extended Thinking
- **⚠ Warning**: Same concern as o1/o3. Extended thinking tokens are billed.
  Compression prompts may cause the model to spend thinking budget on formatting
  rather than problem-solving.
- **Recommendation**: L1 only. Let the model think freely, compress the final output.

### Haiku
- **Compliance**: Excellent. Already terse by nature.
- **Tip**: Haiku is a natural fit for L2/L3. Minimal RLHF verbosity to fight.

---

## Google Models (Gemini 2.5 Pro, Gemini 2.5 Flash)

### Gemini 2.5 Pro
- **Compliance**: Good, but occasionally reverts to verbose mode in long conversations.
- **Tip**: Use `response_schema` in the API for structured output — this is Gemini's
  native structured output and is more token-efficient than prompting for JSON.
- **Override**: Add a mid-conversation reminder: `[Reminder: maintain compressed output style]`
  every 5-8 turns.
- **Bonus**: Gemini's `response_mime_type: "application/json"` forces JSON-only output.

### Gemini 2.5 Flash
- **Compliance**: Very good. Flash models are naturally concise.
- **Tip**: Pair L2/L3 with `response_schema` for maximum savings.

---

## Kimi K2.5 (Moonshot AI)

- **Compliance**: Good for L1/L2, moderate for L3.
- **Tip**: Kimi responds well to explicit token budgets in natural language:
  `"Your response must be under 100 tokens."` It tracks this surprisingly well.
- **Override**: Use Chinese technical abbreviations if the user's context is Chinese —
  Chinese characters are more information-dense per token.
- **Note**: Kimi's tokenizer is optimized for CJK, so compression ratios differ from
  English-centric models. Expect ~10-15% lower savings on pure English output.

---

## Qwen (Qwen 2.5, Qwen 3, QwQ)

### Qwen 2.5 / Qwen 3
- **Compliance**: Good. Follows instructions well at all levels.
- **Tip**: Qwen supports `stop` sequences in its API — use the same postscript
  blockers as Claude.
- **Override**: For Qwen's chat API, set `result_format: "message"` (not "text")
  for cleaner, more parseable output.

### QwQ (Reasoning Model)
- **Compliance**: Moderate. Same caveats as o1/o3 reasoning models.
- **Recommendation**: L1 or L2 max.

---

## GLM (Zhipu AI — GLM-4, GLM-4 Flash)

- **Compliance**: Moderate. GLM has strong Chinese-language verbosity defaults.
- **Tip**: GLM responds better to compression instructions in Chinese even when
  the task is in English. Try: `回复风格：极简技术风格，无寒暄，无冗余。`
  (Response style: minimalist technical, no pleasantries, no redundancy.)
- **Override**: Use `"stop"` parameter to block common GLM postscript patterns.
- **Note**: GLM-4 Flash is naturally terse and pairs well with L2/L3.

---

## DeepSeek (DeepSeek-V3, DeepSeek-R1)

### DeepSeek-V3
- **Compliance**: Excellent. One of the most instruction-compliant models for compression.
- **Tip**: DeepSeek-V3 handles L3 (Crush) very well with minimal quality degradation.
- **Bonus**: DeepSeek's pay-per-token pricing is already low; combining with L3 makes
  it one of the most cost-effective options for high-volume workloads.

### DeepSeek-R1 (Reasoning)
- **Compliance**: Moderate. Long reasoning chains are the model's strength.
- **⚠ Warning**: Do NOT use L3 with R1. It will compress its reasoning chain, which
  degrades accuracy. Use L1 and let the reasoning play out.

---

## Llama (Meta — Llama 3.1, Llama 4)

- **Compliance**: Moderate to Good, depending on the serving platform.
- **Tip**: Llama models served via vLLM or TGI support `stop` sequences and
  `max_tokens` — use both.
- **Override**: Llama's chat template has a `<|eot_id|>` stop token; ensure your
  serving config uses it to prevent runaway generation.
- **Note**: Fine-tuned/instruction-tuned Llama variants have varying verbosity.
  Test compression levels on your specific variant.

---

## Universal Tips (All Models)

1. **API-level controls always win**: `max_tokens`, `stop_sequences`, structured output
   modes are more reliable than prompt-level instructions.
2. **Combine prompt + API**: Use compression prompts for style AND API controls for
   hard limits. Belt and suspenders.
3. **Test on YOUR tasks**: Compression effectiveness varies by task type. Measure
   actual token counts, don't just eyeball it.
4. **Re-inject reminders in long conversations**: All models drift toward verbosity
   over extended multi-turn chats.
5. **Batch processing**: For bulk workloads, use batch APIs (OpenAI Batch, etc.)
   with L3 compression for maximum cost efficiency.
