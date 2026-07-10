# Product Requirements Document: Code Review Assistant

**Version:** 1.0
**Date:** July 9, 2026
**Status:** Draft

---

## 1. Overview

### 1.1 Problem Statement
Developers often lack immediate access to experienced reviewers for quick, explainable feedback on code quality and bugs. This leads to delayed detection of issues, inconsistent review standards, and slower learning. AI-only review tools help, but treat availability as guaranteed — leaving users with nothing when a provider hits an outage, rate limit, or quota cap.

### 1.2 Product Summary
Code Review Assistant is an explanation-first code review tool for individual developers: paste a snippet, get bugs flagged in plain language, and get a usable result even when the AI backend is unavailable — via an automatic, deterministic static-analysis fallback.

### 1.3 Target Users

| Persona | Goals | Frustrations | Context |
|---|---|---|---|
| **Rohan** — Solo Freelancer | Catch bugs before a client does; look competent without a team | AI review tools go silent on outages/rate limits — no fallback, no second opinion | Works across 2–3 client codebases at once, budget near zero |
| **Aditi** — Junior Developer | Understand *why* code is wrong, not just that it is | Linters (ESLint, Pylint) flag issues but never explain them; hesitant to ask seniors "basic" questions | 6 months into first job, still mapping tool output to real understanding |
| **Karan** — Team Lead | Keep review quality consistent across 5 engineers | Review depth varies by reviewer; wary of black-box AI tools he can't explain to stakeholders | Leads a small startup team, answers for shipped bugs |

### 1.4 Value Proposition
For developers who need fast, explainable code review but can't always rely on AI availability, Code Review Assistant delivers LLM-powered bug detection with plain-language explanations, backed by a deterministic static-analysis fallback — unlike AI-only tools that go silent during outages, and unlike traditional linters that never explain why an issue matters.

### 1.5 Competitive Positioning
The market (CodeRabbit, Greptile, Qodo, DeepSource, SonarQube, GitHub Copilot Code Review) is dominated by team-oriented, git-integrated PR bots competing on detection-accuracy benchmarks. Open-source, self-hosted alternatives (PR-Agent, Aider) prove local/zero-API-key review is technically viable but remain CLI/CI-first, not learner-facing. The open gap: a standalone, explanation-first tool for individuals, where **reliability — not raw detection %** — is the core differentiator.

---

## 2. Scope

### 2.1 MVP Scope (Phase 1)
- Paste a single code snippet (Python or JavaScript) — no file upload, no repo cloning
- LLM-powered bug detection with severity labels (bug vs. style) and a plain-language explanation per issue
- Automatic fallback to real static-analysis tools (Pylint / ESLint) on AI failure, timeout, or quota exhaustion
- Single results panel, clearly labeled "AI-reviewed" or "Fallback-reviewed"
- Stateless — no accounts, no login, no saved history

### 2.2 Phase 2
- Multi-file / small folder paste
- Additional language support (Java or Go)
- Save/view past reviews (local storage or lightweight DB)
- Severity/rule tuning (disable style nitpicks)
- Local model (Ollama-style) as a second fallback tier
- Basic per-IP rate-limiting for public deployment

### 2.3 Phase 3
- GitHub/GitLab PR integration (webhooks, OAuth, inline comments)
- Cross-file / whole-codebase, dependency-graph-aware review
- Team accounts, shared history, analytics dashboards
- IDE extension (VS Code)
- User-defined custom rules

### 2.4 Explicitly Out of Scope
Git platform integration of any kind · auto-fix/auto-commit · security/SAST-grade vulnerability scanning · unit test generation · full-codebase dependency analysis · enterprise features (SSO, audit logs, self-hosting) · support beyond 2–3 languages · real-time collaborative review · custom/fine-tuned models · mobile app.

### 2.5 MoSCoW Prioritization

**Must Have** — FR-1 (paste input) · FR-2 (Python/JS support) · FR-3 (severity labels) · FR-4 (explanations) · FR-5 (auto fallback trigger) · FR-6 (real linter fallback engine) · FR-7/NFR-5 (AI-vs-fallback labeling) · NFR-1 (always return a result) · NFR-4 (no code retention)

**Should Have** — FR-8 (single panel) · FR-9 (stateless) · NFR-2 (response time targets) · NFR-3 (jargon-free explanations) · NFR-6 (free-tier budget) · NFR-7 (swappable provider config) · NFR-8 (cross-browser) · consequence-linked explanations (Story 7) · engine visibility (Story 12)

**Could Have** — save/view history (Story 16) · multi-file paste · additional languages · rule tuning · local-model second fallback tier · basic public rate-limiting

**Won't Have (this phase)** — PR integration (Story 17) · auto-fix/commit · SAST scanning · test generation · cross-file analysis · enterprise features · team accounts/multi-tenancy · IDE extension · mobile app · custom rules · multi-user scalability (NFR-9)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | Accept a pasted code snippet (single file) via a text input area |
| FR-2 | Support Python and JavaScript as input languages |
| FR-3 | Return detected issues with a severity label (bug vs. style) |
| FR-4 | Generate a plain-language explanation for every flagged issue |
| FR-5 | Detect AI-call failure (timeout, rate limit, quota, network error) and auto-trigger fallback |
| FR-6 | Run deterministic static analysis (Pylint / ESLint) as the fallback |
| FR-7 | Label each result as "AI-reviewed" or "Fallback-reviewed" |
| FR-8 | Display all issues in a single results panel per request |
| FR-9 | Treat each review as stateless — no login, no persistence (MVP) |

### 3.2 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | Always return *some* result, even under full AI outage — hard requirement |
| NFR-2 | Return reviews within ~10s (AI path) / ~3s (fallback path) for snippets <300 lines |
| NFR-3 | Explanations understandable by a junior developer without external lookup |
| NFR-4 | Pasted code not logged or persisted server-side beyond the request lifetime |
| NFR-5 | AI-vs-fallback source label must be visually unmissable — the core trust signal |
| NFR-6 | Operate within free-tier API quotas for expected MVP demo traffic |
| NFR-7 | LLM provider and fallback linter swappable via config, not hardcoded |
| NFR-8 | Runs in any modern browser, no OS-specific dependencies |
| NFR-9 | Scalability for multi-user public deployment deferred beyond MVP |

---

## 4. User Stories & Acceptance Criteria

### Epic 1: Core Review Flow

**Story 1** — *As a solo developer, I want to paste a code snippet directly, so that I can get feedback without repo/CI setup.*
- Given the input area is filled, when I click "Review," then the system accepts it with no file upload, repo URL, or account required.
- Given the input area is empty, when I click "Review," then submission is blocked with a message prompting me to paste code.

**Story 2** — *As a developer, I want Python and JavaScript support, so that I can use the languages I actually write in.*
- Given valid Python or JS code, when submitted, then the system identifies the language and applies matching review/fallback logic.
- Given an unsupported language, when submitted, then the system clearly states which languages are supported.

**Story 3** — *As a junior developer, I want issues labeled by severity, so that I know what to fix first.*
- Given multiple issues are returned, when displayed, then each shows a visible "Bug" or "Style" tag.
- Given both bug- and style-level issues exist, when viewed, then bugs are prioritized above style issues.

**Story 4** — *As a developer, I want all results in one panel, so that I'm not hunting across tabs.*
- Given a review completes, when results are ready, then all issues appear in a single panel.
- Given zero issues are found, when results are ready, then the panel explicitly states this rather than appearing blank.

### Epic 2: Explanations

**Story 5** — *As a junior developer, I want a plain-language explanation for every bug, so that I understand why it's wrong.*
- Given an issue is flagged, when viewed, then it includes a written explanation, not just a rule ID.
- Given the AI path is used, when an explanation is generated, then it references the specific line/construct involved.

**Story 6** — *As a junior developer, I want jargon-free explanations, so that I don't need external lookups.*
- Given an explanation uses a technical term, when displayed, then the term is briefly defined inline.

**Story 7** — *As a self-taught developer, I want explanations linked to real consequences, so that I build intuition, not memorization.*
- Given a bug is flagged, when explained, then it states the concrete runtime consequence, not just that the pattern is discouraged.

### Epic 3: Reliability & Fallback

**Story 8** — *As a solo freelancer, I want the tool to keep working during AI outages, so that I'm never left with a dead API call.*
- Given the AI provider errors (timeout/rate-limit/quota), when this happens, then the system retries once and falls back automatically, without requiring resubmission.
- Given the fallback is triggered, when results are shown, then the user receives a complete result set, never an empty screen or raw error.

**Story 9** — *As a developer, I want the fallback to use real static-analysis tools, so that I can trust results when AI isn't available.*
- Given the Python fallback path is active, when a review runs, then results come from Pylint (or equivalent).
- Given the JS fallback path is active, when a review runs, then results come from ESLint (or equivalent).

**Story 10** — *As a developer, I want to clearly see the result source, so that I calibrate trust appropriately.*
- Given the AI path produced results, when displayed, then a visible "AI-reviewed" label is shown.
- Given the fallback path produced results, when displayed, then a visible "Fallback-reviewed" label is shown, styled distinctly.

**Story 11** — *As a developer, I want fast fallback responses, so that losing AI access doesn't mean losing my workflow.*
- Given the fallback is triggered, when a snippet under 300 lines is submitted, then results return within ~3 seconds.

### Epic 4: Trust & Consistency

**Story 12** — *As a team lead, I want review logic that isn't a black box, so that I can explain results to stakeholders.*
- Given a result is shown, when inspected, then the specific engine (model or linter/rule) that produced it is visible.

**Story 13** — *As a team lead, I want consistent output across provider changes, so that quality doesn't silently drift.*
- Given the configured LLM provider is swapped, when the same snippet is reviewed, then output format and severity taxonomy stay identical.

### Epic 5: Privacy & Trust

**Story 14** — *As a developer, I want my code not stored after review, so that I can review proprietary code safely.*
- Given a review completes (success or failure), when the response returns, then the code is not written to any persistent log or database.

**Story 15** — *As a developer, I want no account requirement, so that I get a review with zero friction.*
- Given a first-time visit, when I want to run a review, then I am not prompted to sign up or log in.

### Epic 6: Later Phases (backlog — AC to finalize when scoped)

**Story 16** *(Phase 2)* — Save past reviews for tracking recurring mistakes. *Draft AC:* Given a completed review, when saved, then it's retrievable in a history view.

**Story 17** *(Phase 3)* — GitHub PR integration. *Draft AC:* Given a PR opens on a connected repo, when CI triggers review, then results post as inline PR comments.

---

## 5. Risks & Open Issues

### 5.1 Missing / Ambiguous Requirements
- **Cascading failure undefined:** No behavior specified if the fallback engine itself fails (Pylint/ESLint crash, unsupported syntax) — the single point of failure behind NFR-1's entire promise.
- **Malformed AI response:** FR-5 covers timeout/rate-limit/quota, not "200 OK with unparseable output" — a distinct, common LLM failure mode.
- **Hallucination handling:** No defined mitigation for AI flagging non-existent bugs — directly undermines Karan's trust requirement (Story 12).
- **Third-party data retention:** NFR-4 covers server-side logging, not whether the LLM provider itself retains submitted prompts under its own ToS.
- **Public-deploy abuse protection:** Rate-limiting is Could-have, but an unthrottled public demo risks quota exhaustion forcing all users onto fallback, silently breaking the "AI review" half of the demo.
- **Accessibility:** No NFR addresses colorblind-safe severity indicators or screen-reader labels.
- **Severity mapping undefined:** No table maps LLM-judged severity against Pylint/ESLint's built-in categories — risks inconsistent labeling between paths (conflicts with Story 13).
- **Language detection method unspecified:** Auto-detect vs. explicit selector isn't decided; auto-detect has real failure modes (ambiguous JS/TypeScript, JSON blobs).
- **Unquantified limits:** "Typical snippet" (NFR-2) and "expected demo traffic" (NFR-6) have no defined ceilings or numbers.
- **Security-adjacent findings:** Issues like `eval()` usage or hardcoded credentials don't cleanly fit "Bug" vs. "Style" — needs a decision, not a default-by-accident.

### 5.2 Edge Cases
- Syntactically invalid code that breaks the parser entirely (undefined behavior for both engines).
- Partial/out-of-context snippets (e.g., a single function missing imports) causing false positives from missing context.
- Non-code or mixed-content paste (prose, stack traces, Jupyter magics, embedded `<script>` in HTML).
- Same snippet reviewed via AI vs. fallback at different times, producing different (not wrong, just narrower) results — currently undocumented and could look like a bug.
- Already-fixed code pasted back in (relevant once any fix-suggestion display ships in Phase 2+).

### 5.3 Product & Technical Risks

| Risk | Impact | Mitigation |
|---|---|---|
| AI provider deprecation/quota changes (the exact issue that motivated this project) | Core AI path breaks with no warning | NFR-7 (swappable provider config) + fallback is the direct mitigation — keep both current |
| Detection accuracy criticized vs. funded competitors' benchmarks | Reputational, if positioned as an accuracy play | Explicitly position on reliability + explanation quality, not detection % (per competitor scan) |
| False positives erode trust (esp. Karan persona) | Users stop trusting flagged issues | Track/display a confidence signal or "verify before applying" framing |
| Third-party LLM data retention conflicts with privacy promise | Breaks Rohan's core use case (client code) | Document actual provider ToS terms; disclose caveat rather than imply full privacy |
| Single-maintainer / portfolio-project risk | No redundancy if scope grows | Keep MVP scope disciplined; resist Phase 3 features creeping into build before Phase 1 is solid |
| Public demo quota exhaustion | Breaks the AI-path demo for everyone | Promote basic rate-limiting from Could to Must if/when publicly deployed |

---

*This PRD consolidates the problem statement, personas, value proposition, competitive scan, scope definition, requirements, user stories, MoSCoW prioritization, and risk analysis developed for this project.*
