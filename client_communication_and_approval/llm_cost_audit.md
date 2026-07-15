# LLM Cost Audit Report

This report analyzes the token efficiency and operational trade-offs of the AI Code Reviewer Assistant, based on actual logging data captured from production and local test runs.

---

## 1. Model Choice Analysis

*   **Current Configuration**: `llama-3.3-70b-versatile` (configured in [main.py](file:///Users/macbook/repos/practice/backend/main.py#L103)).
*   **Alternative Considered**: An 8B-class model (e.g., `llama-3-8b-8192` or `llama-3.1-8b-instant`).

### Trade-Off Evaluation

| Dimension | Current (70B Model) | Alternative (8B Model) |
| :--- | :--- | :--- |
| **Daily Rate Limit** | **14,400 tokens/day** (Groq free tier). Severe bottleneck. | **1,000,000 tokens/day** (Groq free tier). Virtually eliminates capacity limitations. |
| **Max Requests/Min** | **30 RPM**. Low concurrent capacity. | **30,000 RPM**. High concurrent capacity. |
| **JSON Schema Compliance** | Extremely reliable. Strictly adheres to Pydantic structural boundaries without hallucinations or formatting errors. | Less reliable. High risk of parsing/validation failures on complex JSON returns, causing fallback triggering. |
| **Critique Pragmatism** | Strong reasoning capability; respects senior guidelines (naming, performance) effectively. | Prone to pedantic spirals, generic suggestions, or failing to ground style rules. |

*   **Verdict**: While the rate-limit advantage of the 8B model is massive (nearly 70x capacity), the 70B model's reasoning is critical for structured JSON safety.
*   **Re-Testing Action**: Before switching models in production, the prompt-iteration eval suite ([test_prompt_iteration.py](file:///Users/macbook/repos/practice/backend/tests/test_prompt_iteration.py)) must be run to verify the 8B model passes all test cases (handling empty divisions, ignoring correct type annotations, etc.) and generates valid JSON shapes.

---

## 2. Context Size Audit

Based on real production usage stats from the `/api/usage` endpoint, the system logs the following average metrics per AI call:
*   **Average Prompt Tokens**: **904 tokens**
*   **Average Completion Tokens**: **126 tokens**
*   **Average Total Tokens**: **1,030 tokens**

### Token Breakdown by Component (Measured & Extrapolated)

*   **Base System Prompt (`_SYSTEM_PROMPT_V4`)**: ~601 tokens (~66.5% of prompt).
*   **RAG Style Guide Excerpts (Top-2 Chunks)**: ~227 to 235 tokens (~25.1% of prompt).
*   **User Code Snippet**: ~10 to 31 tokens (~3.4% of prompt).
*   **JSON formatting framing/overhead**: ~40 tokens (~5% of prompt).

### RAG-Retrieved Context Inefficiency

Yes, a concrete inefficiency exists: **the TF-IDF retriever appends the top-2 style guide chunks to every single request unconditionally**, regardless of whether style issues are likely to be found.
*   **Clean Code Call**: For a clean Python snippet like `add_values(x, y)` which has no PEP 8 violations, RAG still prepends **909 characters (~227 tokens)** of style reference guidelines.
*   **Quantified Waste**: This represents **24.2% of the prompt token budget** wasted on calls that return zero style issues.
*   **Impact**: On the Groq free tier (14,400 daily tokens limit), this wasted context limits daily capacity by nearly 25%, translating to ~3.5 fewer reviews per day.

---

## 3. Caching Evaluation

*   **Current State**: No caching is implemented.
*   **Logs Evidence**: Analysis of [task-195.log](file:///Users/macbook/.gemini/antigravity-ide/brain/26587a61-a33c-4a1c-9423-34c3100ee853/.system_generated/tasks/task-195.log) and other test logs confirms that identical code snippets (e.g., the standard `calculate_average` division-by-zero snippet and clean placeholders) were submitted multiple times consecutively during development and testing.
*   **Verdict**: **APPLICABLE**.
    *   **Testing/Development**: Extremely high utility (saves ~1,000 tokens per repeat run during local iterations).
    *   **Production**: Moderate utility. Developers frequently save and re-trigger reviews on unchanged files or make minor edits.
    *   **Recommendation**: A simple, lightweight in-memory cache (like an LRU cache keyed on the MD5 hash of `code + language`) will protect the daily token budget against redundant requests.

---

## 4. Batching Evaluation

*   **Verdict**: **NOT APPLICABLE**.
*   **Reasoning**: The AI Code Reviewer is designed as a real-time interactive tool. A developer requests a code review and expects feedback within 1–2 seconds. Implementing an asynchronous batching queue to aggregate multiple snippets would introduce unacceptable latency and damage the developer experience, with no corresponding saving in token usage.

---

## 5. Deeper Documentation Links

*   **Cost Sheet**: [cost-sheet.md](file:///Users/macbook/repos/practice/client_communication_and_approval/cost-sheet.md)
*   **Monthly Cost Note**: [monthly-cost-note.md](file:///Users/macbook/repos/practice/client_communication_and_approval/monthly-cost-note.md)
*   **Bug Log**: [bug-log.md](file:///Users/macbook/repos/practice/client_communication_and_approval/bug-log.md)
