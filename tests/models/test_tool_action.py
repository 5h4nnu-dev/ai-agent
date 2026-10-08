"""
Test tool action model validation
"""
import pytest
from src.pentest_agent.models.agent import ToolAction


def test_tool_action_creation():
    """Test tool action model creation"""
    tool_action = ToolAction(
        action_id="action_001",
        tool_name="http_request",
        arguments={"url": "https://example.com", "method": "GET"},
        target="https://example.com",
        safety_constraints={}
    )
    assert tool_action.action_id == "action_001"
    assert tool_action.tool_name == "http_request"
    assert tool_action.target == "https://example.com"


def test_tool_action_validation():
    """Test tool action model validation"""
    # This should work without validation errors
    tool_action = ToolAction(
        action_id="action_001",
        tool_name="http_request",
        arguments={"url": "https://example.com", "method": "GET"},
        target="https://example.com",
        safety_constraints={}
    )
    assert tool_action is not None


def test_tool_action_invalid_action_id():
    """Test tool action model with invalid action ID"""
    with pytest.raises(Exception):
        ToolAction(
            action_id="",
            tool_name="http_request",
            arguments={"url": "https://example.com", "method": "GET"},
            target="https://example.com",
            safety_constraints={}
        )


def test_tool_action_invalid_tool_name():
    """Test tool action model with invalid tool name"""
    with pytest.raises(Exception):
        ToolAction(
            action_id="action_001",
            tool_name="",
            arguments={"url": "https://example.com", "method": "GET"},
            target="https://example.com",
            safety_constraints={}
        )


def test_tool_action_invalid_target():
    """Test tool action model with invalid target"""
    with pytest.raises(Exception):
        ToolAction(
            action_id="action_001",
            tool_name="http_request",
            arguments={"url": "https://example.com", "method": "GET"},
            target="",
            safety_constraints={}
        )


if __name__ == "__main__":
    pytest.main([__file__])