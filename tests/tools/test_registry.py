"""
Test tool registry functionality
"""
import pytest
from src.pentest_agent.tools.registry import ToolRegistry
from src.pentest_agent.tools.base import Tool


class MockTool(Tool):
    """Mock tool for testing"""

    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "Mock tool for testing"

    @property
    def input_schema(self):
        return {}

    @property
    def output_schema(self):
        return {}

    def execute(self, input_data):
        return {"result": "success"}


def test_tool_registry_registration():
    """Test tool registration"""
    registry = ToolRegistry()
    tool = MockTool()

    registry.register(tool)
    assert "mock_tool" in registry.list_tools()


def test_tool_registry_lookup():
    """Test tool lookup"""
    registry = ToolRegistry()
    tool = MockTool()

    registry.register(tool)
    retrieved_tool = registry.get_tool("mock_tool")
    assert retrieved_tool.name == "mock_tool"


def test_tool_registry_unknown_tool():
    """Test lookup of unknown tool"""
    registry = ToolRegistry()

    with pytest.raises(ValueError):
        registry.get_tool("unknown_tool")


def test_tool_registry_validation():
    """Test tool action validation"""
    registry = ToolRegistry()
    tool = MockTool()

    registry.register(tool)

    # Should be valid
    assert registry.validate_tool_action("mock_tool", {}) is True

    # Should be invalid
    assert registry.validate_tool_action("unknown_tool", {}) is False


if __name__ == "__main__":
    pytest.main([__file__])