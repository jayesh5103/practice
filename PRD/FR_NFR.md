### Functional Requirements (FR)

| ID | Requirement |
| --- | --- |
| FR-1 | System shall accept a pasted code snippet (single file, not a repo) via a text input area |
| FR-2 | System shall support Python and JavaScript as input languages for the MVP |
| FR-3 | System shall send the snippet to an LLM and return detected bugs/issues with a severity label (bug vs. style) |
| FR-4 | System shall generate a plain-language explanation for each flagged issue, not just a location/label |
| FR-5 | System shall detect AI-call failure (timeout, rate limit, quota exhaustion, network error) and automatically trigger the static-analysis fallback instead of returning an error |
| FR-6 | System shall run deterministic static analysis (Pylint for Python, ESLint for JS) as the fallback path |
| FR-7 | System shall label each result as either "AI-reviewed" or "Fallback-reviewed" so the source is never ambiguous to the user |
| FR-8 | System shall display all flagged issues in a single结果 panel per review request |
| FR-9 | System shall treat each review as stateless — no login, no saved history, no persistence between sessions (MVP only) |

### Non-Functional Requirements (NFR)

| ID | Requirement |
| --- | --- |
| NFR-1 (Reliability) | System shall always return *some* result — a hard requirement, not best-effort — even under full AI outage |
| NFR-2 (Performance) | A typical snippet (<300 lines) shall return a review within ~10 seconds on the AI path, and within ~3 seconds on the fallback path |
| NFR-3 (Usability) | Explanations shall be written at a level a junior developer can understand without external lookup — no unexplained jargon |
| NFR-4 (Privacy) | Pasted code shall not be logged or persisted server-side beyond the lifetime of the request |
| NFR-5 (Transparency) | The AI-vs-fallback source label (FR-7) must be visually unmissable, not a small footnote — it's the core trust signal of the product |
| NFR-6 (Cost) | System shall operate within free-tier API quotas (Gemini/Groq) for expected MVP demo traffic |
| NFR-7 (Maintainability) | LLM provider and fallback linter shall be swappable via config, not hardcoded — protects against the exact quota/deprecation issues that motivated this project |
| NFR-8 (Compatibility) | Frontend shall run in any modern browser with no OS-specific dependencies |
| NFR-9 (Scalability — Phase 2+) | Not required for MVP single-user demo; deferred until multi-user/public deployment is in scope |