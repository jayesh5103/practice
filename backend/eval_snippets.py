"""
eval_snippets.py

Ground-truth eval set for the AI code review prompt.

Each case is a dict with:
  code         – the snippet sent to the model
  language     – "python" or "javascript"
  label        – human-readable name for the case
  expect_flag  – True if we expect at least one issue, False if we expect []
  expect_severity – the severity all flagged issues must have (or None if not checking)
  consequence_keywords – words that must appear in at least one explanation
                         if the case is flagged; tests that the model states a
                         *consequence* ("will throw", "zero", "crash", …) rather
                         than just restating what the code does.

This is a regression set, not a benchmark — four cases cover the properties
we care about at this stage. "All green" means the prompt passes these four
cases; it does not mean general quality is proven.
"""

EVAL_CASES = [
    {
        # ── Case 1: lint-shaped indexing bug ─────────────────────────────────
        # A function that looks safe but crashes on an empty list.
        # A linter *might* flag this with a plugin, but not out of the box.
        # We expect: flagged, severity "bug", explanation mentions empty-list crash.
        "label": "known-lint-shaped bug ([0] access)",
        "language": "python",
        "code": """\
def get_first(items):
    return items[0]
""",
        "expect_flag": True,
        "expect_severity": "bug",
        "consequence_keywords": ["empty", "indexerror", "index", "crash", "raises", "exception"],
    },
    {
        # ── Case 2: non-lint logic bug (division by zero) ─────────────────────
        # This is the MOST IMPORTANT case. Pylint/ESLint will never catch this.
        # The AI's whole justification is flagging exactly this kind of issue.
        # We expect: flagged, severity "bug", explanation mentions "zero" or
        # "empty" and "ZeroDivisionError" or "divide" or similar.
        "label": "non-lint logic bug (division by zero on empty list)",
        "language": "python",
        "code": """\
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
""",
        "expect_flag": True,
        "expect_severity": "bug",
        "consequence_keywords": ["zero", "empty", "division", "zerodivision", "divid", "len"],
    },
    {
        # ── Case 3: clean code → no false positives ───────────────────────────
        # A straightforward, correct function. The model should stay silent.
        # We expect: issues: [].
        "label": "clean code (no issues expected)",
        "language": "python",
        "code": """\
def greet(name: str) -> str:
    \"\"\"Return a greeting for the given name.\"\"\"
    if not name:
        return "Hello, stranger!"
    return f"Hello, {name}!"
""",
        "expect_flag": False,
        "expect_severity": None,
        "consequence_keywords": [],
    },
    {
        # ── Case 4: style-only issue ──────────────────────────────────────────
        # A function that works correctly but uses meaninglessly short variable
        # names. Should be flagged as "style", not "bug".
        # We expect: flagged, severity "style" (not "bug").
        "label": "style-only issue (opaque variable names)",
        "language": "python",
        "code": """\
def calc(a, b, c):
    x = a * b
    y = x + c
    return y
""",
        "expect_flag": True,
        "expect_severity": "style",
        "consequence_keywords": [],
    },
]
