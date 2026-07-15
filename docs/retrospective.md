# Retrospective — Code Review Assistant

## What I Learned

**Reliability is a more defensible pitch than feature breadth.** Against funded, feature-rich competitors (CodeRabbit, Greptile, Qodo), the thing this project could actually own wasn't detection accuracy — it was refusing to fail silently when AI isn't available. That decision, made early, shaped every architectural choice afterward.

**Cross-system consistency (like severity mapping) is genuinely hard, not just tedious.** Mapping an AI's judgment and two different linters' rule categories onto one shared "bug vs. style" scale isn't a solved problem with an obvious right answer — it's a real, debatable engineering call (Pylint `E`/`F` → bug, everything else → style) that I had to actually commit to and document, not something a framework hands you for free.

**Free-tier dependencies are real infrastructure risk, not a minor caveat.** GitHub Models being retired mid-build wasn't a hypothetical scenario I planned around in the abstract — it actually happened, with a 16-day countdown and real brownouts already in progress by the time it surfaced. The provider-swappable config decision (made much earlier, for unrelated reasons) is what turned that from a rewrite into a config change.

**Async code with a blocking call underneath is an easy, specific mistake.** The Pylint/ESLint subprocess calls being synchronous inside an `async def` handler could have silently serialized every concurrent fallback request behind each other — found specifically because the load-check task was designed to look for that exact symptom, not because anyone noticed it by inspection.

## Where AI Helped

- **Speed on structured, well-defined work** — PRDs, user stories, wireframes, task scaffolding, and dozens of well-specified build tasks moved far faster than doing each from scratch.
- **Catching scope conflicts I might have missed under momentum** — CRUD and auth requests both quietly conflicted with the stateless, no-login design (FR-9, Story 15); those got flagged and clarified rather than silently built.
- **Structuring debugging discipline**, not just fixing bugs — reproduce reliably before touching code, form ranked hypotheses before accepting a fix, keep a bug log with a real verified mechanism instead of "it stopped happening." These are habits, not one-off answers, and having them named explicitly made them easier to actually practice.
- **Writing detailed, specific task prompts** rather than vague ones — the difference between "add a fallback" and a task that names the exact subprocess safety requirements, the exact severity mapping, and the exact acceptance criteria was the difference between usable and unusable output from Antigravity.

## Where AI Fell Short (Worth Being Honest About)

- **A mock I wrote myself had a real bug** — the early `setTimeout` mock couldn't detect a genuine Python syntax error, and returned "no issues found" on visibly broken code. I didn't catch that; testing the actual running app did.
- **Screens got designed without a stated requirement behind them** — loading, error, and empty states were built because they matched "good UX instinct," not because a user story asked for them. It took an explicit traceability audit to surface that three separate screens existed with no documented reason, after the fact rather than before.
- **AI-generated output — code, tests, and Antigravity's own task reports — needed independent verification, not trust.** Several tasks specifically required checking Antigravity's own claims (the cache/fallback interaction test, the "confirm production actually has these changes" checks) rather than accepting a self-reported "done."
- **Non-determinism made "did the fix work" a genuinely harder question than in ordinary code.** The same AI call can behave differently run to run, which meant "reproduce reliably" sometimes meant tracking a failure *rate*, not a fixed reproduction — a real added layer of difficulty that traditional debugging advice doesn't usually cover.

## Next Goals

- Stress-test the severity mapping against more real Pylint output, specifically the `W`-category assumption that's currently a named-but-unverified judgment call.
- Investigate whether the RAG retrieval's "embed the code as the query" approach is actually retrieving the right style-guide chunk often enough, or whether it needs a better query strategy.
- Expand language support beyond Python/JS, now that the core reliability and explanation mechanics are proven out.
- Turn the actual decision-making process here — reliability-over-features, the honest prompt-vs-RAG-vs-fine-tune framework, the free-tier dependency near-miss — into a written artifact (blog post or portfolio writeup) separate from the code itself. The story of the decisions is arguably as valuable for interviews as the working product.
