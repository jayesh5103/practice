# Code Review Assistant — Product Brief

**One-liner:** An explanation-first code review tool for individual developers — paste code, get bugs flagged in plain language, and never get *nothing back*, even when the AI backend is down.

## Problem

Developers working solo or without ready access to a senior reviewer lack fast, explainable feedback on their code. Existing tools either flag issues without explaining them (linters), or are built for team PR workflows with per-seat pricing and git-platform lock-in (CodeRabbit, Greptile, Qodo) — none are designed around a single learner reading one file closely, and none treat "AI is unavailable" as a first-class product state.

## Target Users

| Persona | Need | Frustration |
|---|---|---|
| **Rohan**, solo freelancer | Catch bugs before a client does | AI review tools go silent on rate limits/outages — no fallback |
| **Aditi**, junior developer | Understand *why* code is wrong, not just that it is | Linters flag issues but never explain them |
| **Karan**, team lead | Consistent review quality across the team | Review depth varies by reviewer; wary of black-box AI tools |

## Value Proposition

For developers who need fast, explainable code review but can't always rely on AI availability, Code Review Assistant delivers LLM-powered bug detection with plain-language explanations, backed by a deterministic static-analysis fallback — unlike AI-only tools that go silent during outages, and unlike traditional linters that never explain why an issue matters.

## Competitive Positioning

The market (CodeRabbit, Greptile, Qodo, DeepSource, SonarQube) is saturated with team-oriented, git-integrated PR bots competing on detection-accuracy benchmarks. The open gap: a standalone, explanation-first tool for individuals, with reliability — not raw detection %, which is a contested benchmark war — as the core differentiator.

## MVP Scope

- Paste a single snippet (Python or JavaScript)
- LLM-powered bug detection + plain-language explanation per issue
- Automatic fallback to real static-analysis tools (Pylint/ESLint) if the AI call fails, times out, or hits quota
- One result panel, clearly labeled AI-reviewed vs. fallback-reviewed
- Stateless — no accounts, no saved history

## Explicitly Out of Scope (MVP)

Git/PR integration, auto-fix/commit, security/SAST-grade scanning, unit test generation, cross-file/whole-codebase analysis, enterprise features (SSO, audit logs, self-hosting), support for more than 2–3 languages, mobile app.

## Success Signal

A working demo that (1) reviews genuinely buggy code with useful explanations, and (2) demonstrably falls back gracefully when the API key is pulled — proving the reliability differentiator, not just the AI feature.