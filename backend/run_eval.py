"""
run_eval.py

Lightweight eval script for the AI code review prompt.

Usage:
    python3 run_eval.py              # uses the active prompt (v2)
    python3 run_eval.py --prompt v1  # uses the first-draft prompt for comparison

Each case is run through the GitHub Models API via the openai SDK
(reads GITHUB_TOKEN from .env).
For each case, three properties are checked:
  1. flagged-or-not  – did the model flag when we expected it to (or stay silent)?
  2. severity match  – if flagged, does severity match what we expect?
  3. consequence     – if flagged, does the explanation mention the actual failure
                       condition (not just a restatement of the code)?

Exit code 0 if all checks pass, 1 if any fail — suitable for CI.
"""

import argparse
import json
import os
import sys
import textwrap

from dotenv import load_dotenv
from groq import Groq

from eval_snippets import EVAL_CASES
from prompts import build_system_prompt, build_system_prompt_v1, build_system_prompt_v2, build_system_prompt_v3

load_dotenv()

_AI_MODEL = "llama-3.3-70b-versatile"
_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# ---------------------------------------------------------------------------
# Colours (ANSI) — degrade gracefully on terminals that don't support them
# ---------------------------------------------------------------------------

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _ok(msg: str) -> str:
    return f"{GREEN}✓ PASS{RESET}  {msg}"


def _fail(msg: str) -> str:
    return f"{RED}✗ FAIL{RESET}  {msg}"


def _warn(msg: str) -> str:
    return f"{YELLOW}~ SKIP{RESET}  {msg}"


# ---------------------------------------------------------------------------
# Core eval logic
# ---------------------------------------------------------------------------

def call_model(code: str, language: str, prompt_builder) -> list[dict]:
    """
    Call the GitHub Models API with the given prompt builder.

    Returns a list of raw issue dicts on success.
    Raises on any API/parsing error — the caller decides how to handle.
    """
    response = _client.chat.completions.create(
        model=_AI_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": prompt_builder(language)},
            {"role": "user",   "content": code},
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model wraps its JSON in them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)
    return parsed["issues"]


def evaluate_case(case: dict, prompt_builder, prompt_label: str) -> tuple[bool, list[str]]:
    """
    Run one eval case and return (all_passed, list_of_result_lines).
    """
    label          = case["label"]
    code           = case["code"]
    language       = case["language"]
    expect_flag    = case["expect_flag"]
    expect_sev     = case["expect_severity"]
    keywords       = case["consequence_keywords"]

    lines = []
    lines.append(f"\n{BOLD}Case: {label}{RESET}  [{prompt_label}]")
    lines.append(f"  Code:\n{textwrap.indent(code.strip(), '    ')}")

    all_passed = True

    # ── API call ──────────────────────────────────────────────────────────────
    try:
        issues = call_model(code, language, prompt_builder)
    except Exception as exc:
        lines.append(_fail(f"API/parsing error: {type(exc).__name__}: {exc}"))
        return False, lines

    # Pretty-print what the model returned
    if issues:
        lines.append(f"  Model returned {len(issues)} issue(s):")
        for i, iss in enumerate(issues, 1):
            lines.append(f"    [{i}] severity={iss.get('severity')!r}  title={iss.get('title')!r}")
            expl = iss.get("explanation", "")
            lines.append(f"        {textwrap.fill(expl, width=90, subsequent_indent='        ')}")
            if fix := iss.get("fix"):
                lines.append(f"        fix: {textwrap.fill(fix, width=86, subsequent_indent='              ')}")
    else:
        lines.append("  Model returned: issues: []")

    # ── Check 1: flagged-or-not ───────────────────────────────────────────────
    was_flagged = len(issues) > 0
    if expect_flag and was_flagged:
        lines.append(_ok("flagged (expected)"))
    elif not expect_flag and not was_flagged:
        lines.append(_ok("silent (expected — no false positive)"))
    elif expect_flag and not was_flagged:
        lines.append(_fail("expected at least one issue — model returned []"))
        all_passed = False
    else:
        lines.append(_fail(f"expected no issues — model returned {len(issues)}"))
        all_passed = False

    # ── Check 2: severity match ───────────────────────────────────────────────
    if expect_sev is None or not expect_flag:
        lines.append(_warn("severity check skipped (not applicable for this case)"))
    elif was_flagged:
        actual_sevs = {iss.get("severity") for iss in issues}
        if expect_sev == "bug":
            # At least one bug must be flagged. Additional style issues alongside
            # a real bug are acceptable (and expected from a pedantic prompt).
            if "bug" in actual_sevs:
                lines.append(_ok(f"at least one {expect_sev!r} severity found (expected)"))
            else:
                lines.append(_fail(f"expected at least one {expect_sev!r} severity, got {sorted(actual_sevs)}"))
                all_passed = False
        else:
            # Style cases: ALL issues must be "style" — no false-bug labels on
            # code that is behaviourally correct.
            if all(s == expect_sev for s in actual_sevs):
                lines.append(_ok(f"all severities are {expect_sev!r} (expected)"))
            else:
                wrong = sorted(s for s in actual_sevs if s != expect_sev)
                lines.append(_fail(f"expected all severities to be {expect_sev!r}, got bug(s) on correct code: {wrong}"))
                all_passed = False
    else:
        lines.append(_warn("severity check skipped (model was silent)"))

    # ── Check 3: consequence in explanation ───────────────────────────────────
    if not keywords or not expect_flag:
        lines.append(_warn("consequence check skipped (no keywords defined for this case)"))
    elif was_flagged:
        all_text = " ".join(
            iss.get("explanation", "").lower() for iss in issues
        )
        matched = [kw for kw in keywords if kw in all_text]
        if matched:
            lines.append(_ok(f"explanation mentions consequence keyword(s): {matched}"))
        else:
            lines.append(
                _fail(
                    f"explanation does not mention any expected consequence keywords "
                    f"{keywords!r} — may be restating the code rather than the failure"
                )
            )
            all_passed = False
    else:
        lines.append(_warn("consequence check skipped (model was silent)"))

    return all_passed, lines


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run the code review prompt eval")
    parser.add_argument(
        "--prompt",
        choices=["v1", "v2", "v3", "v4"],
        default="v4",
        help="Which prompt version to evaluate (default: v4)",
    )
    args = parser.parse_args()

    if args.prompt == "v1":
        prompt_builder = build_system_prompt_v1
        prompt_label = "v1 (first-draft)"
    elif args.prompt == "v2":
        prompt_builder = build_system_prompt_v2
        prompt_label = "v2 (logic-bug focus)"
    elif args.prompt == "v3":
        prompt_builder = build_system_prompt_v3
        prompt_label = "v3 (pedantic reviewer)"
    else:
        prompt_builder = build_system_prompt
        prompt_label = "v4 (pragmatic reviewer)"

    print(f"\n{BOLD}{'='*72}{RESET}")
    print(f"{BOLD}Code Review Prompt Eval — {prompt_label}{RESET}")
    print(f"{BOLD}{'='*72}{RESET}")
    print(f"Running {len(EVAL_CASES)} cases against {_AI_MODEL} ...\n")

    total   = len(EVAL_CASES)
    passed  = 0
    failed  = 0

    for case in EVAL_CASES:
        ok, output_lines = evaluate_case(case, prompt_builder, prompt_label)
        for line in output_lines:
            print(line)
        if ok:
            passed += 1
        else:
            failed += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{'='*72}{RESET}")
    summary_colour = GREEN if failed == 0 else RED
    print(
        f"{summary_colour}{BOLD}Results [{prompt_label}]: "
        f"{passed}/{total} cases passed, {failed} failed{RESET}"
    )
    print(f"{BOLD}{'='*72}{RESET}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
