"""
Unit tests for app.services.prompt_engineering — pure functions, no
database or event loop needed, so these run instantly without the
Postgres fixtures the rest of the suite requires.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.prompt_engineering import build_system_prompt, detect_mode  # noqa: E402


def test_detect_mode_academic_for_programming_question():
    assert detect_mode("Can you explain how a linked list works in Python?") == "academic"


def test_detect_mode_department_for_registration_question():
    assert detect_mode("How do I register my courses this semester?") == "department"


def test_detect_mode_campus_for_hostel_question():
    assert detect_mode("How do I apply for a hostel at the polytechnic?") == "campus"


def test_detect_mode_defaults_to_department_when_ambiguous():
    assert detect_mode("hello") == "department"


def test_build_system_prompt_never_leaks_admin_override_as_knowledge():
    prompt = build_system_prompt("academic", knowledge_context="", admin_override="Custom admin prompt")
    assert "Custom admin prompt" in prompt
    assert "No knowledge base context was found" in prompt


def test_build_system_prompt_includes_knowledge_context_when_present():
    prompt = build_system_prompt("department", knowledge_context="[FAQ] Q: test\nA: answer")
    assert "[FAQ] Q: test" in prompt
    assert "No knowledge base context was found" not in prompt
