# Cost Sheet — Code Review Assistant (AI Path)

Pricing confirmed against Anthropic's current published rates at time of writing. Estimates below should be replaced with real measured numbers once token logging (see companion Antigravity task) is running.

## Model and Rates

`claude-haiku-4-5-20251001` — $1.00 per million input tokens, $5.00 per million output tokens.

## Per-Call Estimate

| Component | Estimate | Basis |
|---|---|---|
| System prompt + RAG-grounding context | ~400–500 tokens | Prompt from the prompt-iteration task, plus retrieved style-guide chunks when style issues apply |
| Code snippet (input) | ~150–400 tokens | Typical 20–50 line snippet, well under the 500-line input cap |
| **Total input** | **~800 tokens** | |
| Output (JSON, 1–3 issues) | ~200–300 tokens | |
| **Estimated cost per call** | **~$0.0018–0.002** | (800 × $1/M) + (250 × $5/M) |

## Cost Per 1,000 Users, by Usage Assumption

| Usage pattern | Reviews/user/month | Estimated cost per 1,000 users/month |
|---|---|---|
| Light — occasional check-ins | 3 | ~$6 |
| Moderate — regular use during active dev | 10 | ~$20 |
| Heavy — frequent, throughout the day | 30 | ~$60 |

## Caveats

- Only the AI path has a token cost — fallback-only reviews (real Pylint/ESLint) cost nothing.
- These are pre-measurement estimates. Once token logging is in place, replace this table with real averages from actual traffic.
- Anthropic's pricing is current as of this writing but subject to change — this sheet has a shelf life and should be revisited periodically, not treated as permanent.
- Usage pattern (light/moderate/heavy) is the single biggest unknown here — actual cost depends far more on real adoption than on anything technical in this sheet.
