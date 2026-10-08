"""
Test test plan model validation
"""
import pytest
from src.pentest_agent.models.agent import TestPlan


def test_test_plan_creation():
    """Test test plan model creation"""
    test_plan = TestPlan(
        test_id="test_001",
        target="https://example.com",
        vulnerability_category="prompt_injection",
        objective="Test for direct prompt injection",
        requested_tool_action={"tool": "http_request", "url": "https://example.com/api"},
        parameters={"timeout": "10"},
        priority="high",
        reasoning="Direct injection is a critical vulnerability"
    )
    assert test_plan.test_id == "test_001"
    assert test_plan.priority == "high"


def test_test_plan_validation():
    """Test test plan model validation"""
    # This should work without validation errors
    test_plan = TestPlan(
        test_id="test_001",
        target="https://example.com",
        vulnerability_category="prompt_injection",
        objective="Test for direct prompt injection",
        requested_tool_action={"tool": "http_request", "url": "https://example.com/api"},
        parameters={"timeout": "10"},
        priority="high",
        reasoning="Direct injection is a critical vulnerability"
    )
    assert test_plan is not None


def test_test_plan_invalid_priority():
    """Test test plan model with invalid priority"""
    with pytest.raises(Exception):
        TestPlan(
            test_id="test_001",
            target="https://example.com",
            vulnerability_category="prompt_injection",
            objective="Test for direct prompt injection",
            requested_tool_action={"tool": "http_request", "url": "https://example.com/api"},
            parameters={"timeout": "10"},
            priority="invalid_priority",
            reasoning="Direct injection is a critical vulnerability"
        )


def test_test_plan_invalid_text_fields():
    """Test test plan model with invalid text fields"""
    with pytest.raises(Exception):
        TestPlan(
            test_id="test_001",
            target="https://example.com",
            vulnerability_category="",
            objective="Test for direct prompt injection",
            requested_tool_action={"tool": "http_request", "url": "https://example.com/api"},
            parameters={"timeout": "10"},
            priority="high",
            reasoning="Direct injection is a critical vulnerability"
        )


if __name__ == "__main__":
    pytest.main([__file__])