# Changelog & Release Notes

## [v1.0.0] - 2026-07-15

This is the initial production-ready release of the AI-Powered Code Reviewer application. It represents a fully tested, integrated, and deployed milestone of the dual-path architecture.

---

### What's Included

#### 1. Core AI-Driven Code Review
*   Integrates with **Groq Cloud API** running `llama-3.3-70b-versatile` to provide pragmatic, senior-level code reviews.
*   Enforces strict structured JSON schema responses containing an `issues` array of style and bug suggestions.

#### 2. Dual-Path Reliability Guarantee
*   Implements automatic, graceful degradation to **local linters (Pylint for Python, ESLint for JavaScript)** running as subprocesses.
*   If the Groq API fails (due to key expiration, server timeouts, network issues, or rate limits), the review is resolved via static analysis, guaranteeing the user never sees a blank screen or raw API error.

#### 3. Style Guide Grounding (RAG)
*   Integrates a local **TF-IDF vector database** populated with official style guide rules (PEP 8 for Python, standard guidelines for JavaScript).
*   Retrieves style rules matching code keywords and injects them into the LLM system prompt, forcing AI suggestions to reference official rules (e.g. *"Per PEP 8 naming conventions..."*).

#### 4. Interactive Web Interface
*   **React Frontend** (Vercel-hosted) with a premium dark-mode dashboard.
*   Implements **5 user-interface screen states**:
    *   *Input State*: Code input form with language selector.
    *   *Loading State*: Clean spinner with micro-animations.
    *   *Review Success State*: Structured panels showing bugs/style warnings with code explanations and fixes.
    *   *Zero Issues State*: Clean "No issues found" screen.
    *   *Error Fallback State*: Graceful error panel showing diagnostic logs and a "Retry" trigger.

#### 5. Cost-Saving Optimizations
*   **RAG retrieve top_k = 1**: Saves **110.7 prompt tokens per call (11.7% cost reduction)**.
*   **Ephemeral Request Cache**: Thread-safe in-memory caching keyed by MD5 of `code + language`, preventing duplicate API requests for identical code submissions.

#### 6. Operations & Monitoring
*   Structured JSON logging with request **correlation IDs** for lifecycle tracing.
*   In-memory usage quota tracker with automated **Discord Webhook alerting** when request counts hit 80% of the daily limit.

#### 7. Verification Suite
*   Backend Python Unit & Integration test suite (`pytest`) -> **16/16 passed**.
*   Frontend Unit tests (`Vitest`) -> **11/11 passed**.
*   End-to-End browser tests (`Playwright`) -> **2/2 passed**.

---

### Known Limitations & Trade-offs

*   **Severity Mapping Decision**: Categorizing lint findings into `bug` or `style` is a subjective engineering design choice, not a strict compiler rule. It was chosen to align with the visual styling of the user dashboard.
*   **TF-IDF Retrieval Simplification**: The RAG retriever is a lightweight local vectorizer. While highly performant and free of network latency, it does not perform semantic/embedding search.
*   **Render Cold-Start Latency**: The production backend is deployed on **Render's free tier**, which spins down the container after 15 minutes of inactivity. The first request after a spin-down experiences a **30-60 second delay**.
*   **In-Memory Usage Quota**: The usage quota counter and 80% alert flag reside in-memory. Consequently, Render's container restarts or cold starts reset this count to zero.
