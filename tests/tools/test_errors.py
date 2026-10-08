"""
Test tool error handling
"""
import pytest
from src.pentest_agent.tools.errors import ToolError, ERROR_TYPES


def test_tool_error_creation():
    """Test tool error creation"""
    error = ToolError(
        error_type="scope_violation",
        message="Attempted to access external domain",
        details="External domain not in scope",
        timestamp="2023-01-01T00:00:00Z"
    )
    assert error.error_type == "scope_violation"
    assert error.message == "Attempted to access external domain"
    assert error.details == "External domain not in scope"
    assert error.timestamp == "2023-01-01T00:00:00Z"


def test_error_types():
    """Test error type definitions"""
    assert "scope_violation" in ERROR_TYPES
    assert "validation_error" in ERROR_TYPES
    assert "timeout" in ERROR_TYPES


if __name__ == "__main__":
    pytest.main([__file__])