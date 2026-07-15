import pytest
import sys
import os

# Add parent directory to path so main can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import map_severity, validate_input_length, validate_ai_response, Issue
from rag.retriever import retrieve

# ---------------------------------------------------------------------------
# map_severity tests
# ---------------------------------------------------------------------------

def test_map_severity_pylint():
    """
    Ensure Pylint severity categories (full names and letters) map correctly to "bug" or "style".
    """
    assert map_severity("error", "pylint") == "bug"
    assert map_severity("fatal", "pylint") == "bug"
    assert map_severity("e", "pylint") == "bug"
    assert map_severity("f", "pylint") == "bug"
    
    assert map_severity("convention", "pylint") == "style"
    assert map_severity("refactor", "pylint") == "style"
    assert map_severity("warning", "pylint") == "style"
    assert map_severity("c", "pylint") == "style"
    assert map_severity("r", "pylint") == "style"
    assert map_severity("w", "pylint") == "style"  # KeyError regression case

def test_map_severity_eslint():
    """
    Ensure ESLint severity levels (numbers and names) map correctly to "bug" or "style".
    """
    assert map_severity("2", "eslint") == "bug"
    assert map_severity("error", "eslint") == "bug"
    
    assert map_severity("1", "eslint") == "style"
    assert map_severity("warning", "eslint") == "style"
    assert map_severity("warn", "eslint") == "style"

def test_map_severity_errors():
    """
    Validate error handling for unknown categories or unknown linter engines.
    """
    with pytest.raises(KeyError):
        map_severity("unknown", "pylint")
    with pytest.raises(KeyError):
        map_severity("3", "eslint")
    with pytest.raises(ValueError):
        map_severity("error", "unknown-engine")


# ---------------------------------------------------------------------------
# validate_input_length tests
# ---------------------------------------------------------------------------

def test_validate_input_length_lines():
    """
    Ensure boundary limits on line counts (under, at, and over the 500 lines cap).
    """
    # 499 lines: Valid
    assert validate_input_length("\n" * 498) is True
    # 500 lines: Valid (exactly at boundary)
    assert validate_input_length("\n" * 499) is True
    # 500 lines (exactly at limit): Valid
    assert validate_input_length("\n" * 500) is True
    # 501 lines (over boundary): Invalid
    assert validate_input_length("\n" * 501) is False




def test_validate_input_length_chars():
    """
    Ensure boundary limits on characters (under, at, and over the 10,000 character cap).
    """
    # 9,999 characters: Valid
    assert validate_input_length("a" * 9999) is True
    # 10,000 characters: Valid
    assert validate_input_length("a" * 10000) is True
    # 10,001 characters: Invalid
    assert validate_input_length("a" * 10001) is False


# ---------------------------------------------------------------------------
# validate_ai_response tests
# ---------------------------------------------------------------------------

def test_validate_ai_response_valid():
    """
    Ensure a fully compliant structured issue list passes validation successfully.
    """
    valid_payload = {
        "issues": [
            {
                "severity": "bug",
                "title": "Index Error",
                "explanation": "Out of bounds access on empty list",
                "fix": "Add check: if items"
            },
            {
                "severity": "style",
                "title": "Bad naming",
                "explanation": "Variable 'x' is too vague",
                "fix": None
            }
        ]
    }
    validated = validate_ai_response(valid_payload)
    assert len(validated) == 2
    assert validated[0].severity == "bug"
    assert validated[1].severity == "style"

def test_validate_ai_response_invalid_severity():
    """
    Ensure validation fails if the AI returns an unsupported severity value.
    """
    payload = {"issues": [{"severity": "info", "title": "A", "explanation": "B"}]}
    with pytest.raises(ValueError, match="invalid severity"):
        validate_ai_response(payload)

def test_validate_ai_response_empty_fields():
    """
    Ensure empty titles or explanations are rejected.
    """
    payload_empty_title = {"issues": [{"severity": "bug", "title": "", "explanation": "B"}]}
    payload_empty_expl = {"issues": [{"severity": "bug", "title": "A", "explanation": " "}]}
    
    with pytest.raises(ValueError, match="invalid, empty, or too long title"):
        validate_ai_response(payload_empty_title)
    with pytest.raises(ValueError, match="invalid, empty, or too long explanation"):
        validate_ai_response(payload_empty_expl)

def test_validate_ai_response_oversized_text():
    """
    Ensure titles, explanations, or fixes over 300 characters are rejected.
    """
    payload_long_title = {"issues": [{"severity": "bug", "title": "a" * 301, "explanation": "B"}]}
    payload_long_expl = {"issues": [{"severity": "bug", "title": "A", "explanation": "b" * 301}]}
    payload_long_fix = {"issues": [{"severity": "bug", "title": "A", "explanation": "B", "fix": "c" * 301}]}
    
    with pytest.raises(ValueError, match="too long title"):
        validate_ai_response(payload_long_title)
    with pytest.raises(ValueError, match="too long explanation"):
        validate_ai_response(payload_long_expl)
    with pytest.raises(ValueError, match="too long fix"):
        validate_ai_response(payload_long_fix)

def test_validate_ai_response_array_bounds():
    """
    Ensure validation caps issues list size to exactly 20.
    """
    # 20 issues: Valid
    valid_issues = {"issues": [{"severity": "bug", "title": "A", "explanation": "B"}] * 20}
    assert len(validate_ai_response(valid_issues)) == 20
    
    # 21 issues: Invalid
    invalid_issues = {"issues": [{"severity": "bug", "title": "A", "explanation": "B"}] * 21}
    with pytest.raises(ValueError, match="exceeds the limit of 20"):
        validate_ai_response(invalid_issues)

def test_validate_ai_response_non_list():
    """
    Ensure validation fails when the issues key is not a list.
    """
    payload_non_list = {"issues": "not-a-list"}
    with pytest.raises(ValueError, match="is not a list"):
        validate_ai_response(payload_non_list)


# ---------------------------------------------------------------------------
# RAG Similarity tests
# ---------------------------------------------------------------------------

def test_rag_similarity():
    """
    Verify that a keyword-rich query successfully retrieves the intended style doc rule
    over unrelated ones using the actual PEP 8 guidelines.
    """
    # Retrieve top 2 chunks for python
    results = retrieve("type annotations PEP 484 functions parameter return type hints", "python", top_k=2)
    assert len(results) > 0
    # The top matching rule should be pep8 #4 which explicitly details Type Annotations
    top_labels = [r["label"] for r in results]
    assert "pep8 #4" in top_labels
    # The score should be reasonably significant compared to unrelated rules
    pep8_4_score = next(r["score"] for r in results if r["label"] == "pep8 #4")
    assert pep8_4_score > 0.05
