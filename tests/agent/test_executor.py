"""
Tests for the Agent Executor component
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.pentest_agent.agent.executor import AgentExecutorImpl
from src.pentest_agent.tools.registry import ToolRegistry
from src.pentest_agent.tools.base import Tool
from src.pentest_agent.models.agent import TestPlan, ToolAction
from src.pentest_agent.models.scan import ScanConfig, Target
from src.pentest_agent.models.tool import ToolResult


class MockHTTPTool(Tool):
    """Mock HTTP tool for testing"""

    @property
    def name(self) -> str:
        return "http_request"

    @property
    def description(self) -> str:
        return "Mock HTTP tool for testing"

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "headers": {"type": "object"},
                "body": {"type": "string"},
                "timeout": {"type": "number", "minimum": 1, "maximum": 30}
            },
            "required": ["url", "method"]
        }

    @property
    def output_schema(self):
        return {
            "type": "object",
            "properties": {
                "status_code": {"type": "integer"},
                "body": {"type": "string"}
            }
        }

    def execute(self, input_data):
        # Simple mock execution
        return {
            "status_code": 200,
            "body": "test response",
            "url": input_data.get("url", ""),
            "method": input_data.get("method", "")
        }


class MockCrawlTool(Tool):
    """Mock crawl tool for testing"""

    @property
    def name(self) -> str:
        return "crawl"

    @property
    def description(self) -> str:
        return "Mock crawl tool for testing"

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "base_url": {"type": "string", "format": "uri"},
                "max_depth": {"type": "integer", "minimum": 0, "maximum": 3},
                "max_pages": {"type": "integer", "minimum": 0, "maximum": 100}
            },
            "required": ["base_url", "max_depth", "max_pages"]
        }

    @property
    def output_schema(self):
        return {
            "type": "object",
            "properties": {
                "discovered_endpoints": {"type": "array"},
                "discovered_forms": {"type": "array"},
                "discovered_parameters": {"type": "array"}
            }
        }

    def execute(self, input_data):
        # Simple mock execution
        return {
            "discovered_endpoints": [],
            "discovered_forms": [],
            "discovered_parameters": [],
            "status_code": 200
        }


def test_executor_initialization():
    """Test executor initialization"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)
    assert executor.tool_registry == mock_registry


def test_validate_execution():
    """Test execution validation"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Test valid action
    valid_action = {
        "action_id": "action123",
        "tool_name": "mock_tool",
        "target": "http://example.com"
    }

    assert executor.validate_execution(valid_action) is True

    # Test invalid action (missing required fields)
    invalid_action = {
        "action_id": "action123",
        "tool_name": "mock_tool"
        # Missing target
    }

    assert executor.validate_execution(invalid_action) is False

    # Test invalid action (not a dict)
    assert executor.validate_execution("not_a_dict") is False


def test_execute_unknown_tool():
    """Test execution with unknown tool name"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.get_tool.side_effect = ValueError("Unknown tool: invalid_tool")

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Create a test plan with unknown tool using direct dict approach
    tool_action_data = {
        "action_id": "action123",
        "tool_name": "invalid_tool",
        "arguments": {"url": "http://example.com", "method": "GET"},
        "target": "http://example.com",
        "safety_constraints": {}
    }

    plan = TestPlan(
        test_id="test123",
        target="http://example.com",
        vulnerability_category="Prompt Injection",
        objective="Test prompt injection",
        requested_tool_action=tool_action_data,
        parameters={},
        priority="high",
        reasoning="Test reasoning"
    )

    # Create scan config
    scan_config = ScanConfig(
        target=Target(url="http://example.com", scheme="http", host="example.com", port=80, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    # Execute the plan
    results = executor.execute(plan, scan_config)

    # Should return one failed result
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_id == "action123"
    assert "Unknown tool" in results[0].status


def test_execute_invalid_tool_arguments():
    """Test execution with invalid tool arguments"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Create a mock tool
    mock_tool = MockHTTPTool()
    mock_registry.get_tool.return_value = mock_tool

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Create a test plan with invalid arguments (missing required method)
    tool_action_data = {
        "action_id": "action123",
        "tool_name": "http_request",
        "arguments": {"url": "http://example.com"},  # Missing method
        "target": "http://example.com",
        "safety_constraints": {}
    }

    plan = TestPlan(
        test_id="test123",
        target="http://example.com",
        vulnerability_category="Prompt Injection",
        objective="Test prompt injection",
        requested_tool_action=tool_action_data,
        parameters={},
        priority="high",
        reasoning="Test reasoning"
    )

    # Create scan config
    scan_config = ScanConfig(
        target=Target(url="http://example.com", scheme="http", host="example.com", port=80, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    # Execute the plan
    results = executor.execute(plan, scan_config)

    # Should return one failed result due to invalid arguments
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_id == "action123"
    assert "Invalid tool arguments" in results[0].status


def test_execute_out_of_scope_target():
    """Test execution with out-of-scope target"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Create a mock tool
    mock_tool = MockHTTPTool()
    mock_registry.get_tool.return_value = mock_tool

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Create a test plan with out-of-scope target
    tool_action_data = {
        "action_id": "action123",
        "tool_name": "http_request",
        "arguments": {"url": "http://attacker.com", "method": "GET"},
        "target": "http://attacker.com",
        "safety_constraints": {}
    }

    plan = TestPlan(
        test_id="test123",
        target="http://example.com",
        vulnerability_category="Prompt Injection",
        objective="Test prompt injection",
        requested_tool_action=tool_action_data,
        parameters={},
        priority="high",
        reasoning="Test reasoning"
    )

    # Create scan config with target scope
    scan_config = ScanConfig(
        target=Target(url="http://example.com", scheme="http", host="example.com", port=80, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    # Execute the plan
    results = executor.execute(plan, scan_config)

    # Should return one failed result due to scope violation
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_id == "action123"
    assert "Scope violation" in results[0].status


def test_execute_disallowed_http_method():
    """Test execution with disallowed HTTP method"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Create a mock tool
    mock_tool = MockHTTPTool()
    mock_registry.get_tool.return_value = mock_tool

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Create a test plan with disallowed method
    tool_action_data = {
        "action_id": "action123",
        "tool_name": "http_request",
        "arguments": {"url": "http://example.com", "method": "HEAD"},  # HEAD not allowed
        "target": "http://example.com",
        "safety_constraints": {}
    }

    plan = TestPlan(
        test_id="test123",
        target="http://example.com",
        vulnerability_category="Prompt Injection",
        objective="Test prompt injection",
        requested_tool_action=tool_action_data,
        parameters={},
        priority="high",
        reasoning="Test reasoning"
    )

    # Create scan config
    scan_config = ScanConfig(
        target=Target(url="http://example.com", scheme="http", host="example.com", port=80, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    # Execute the plan
    results = executor.execute(plan, scan_config)

    # Should return one failed result due to validation error (tool schema validation catches the invalid method)
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_id == "action123"
    # The error now comes from tool argument validation, not HTTP method validation specifically
    assert "Invalid tool arguments" in results[0].status


def test_execute_scan_budget_exceeded():
    """Test execution when scan budget is exceeded"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Create a mock tool
    mock_tool = MockHTTPTool()
    mock_registry.get_tool.return_value = mock_tool

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Manually set action count to maximum to simulate budget exceeded
    executor._action_count = 100

    # Create a test plan
    tool_action_data = {
        "action_id": "action123",
        "tool_name": "http_request",
        "arguments": {"url": "http://example.com", "method": "GET"},
        "target": "http://example.com",
        "safety_constraints": {}
    }

    plan = TestPlan(
        test_id="test123",
        target="http://example.com",
        vulnerability_category="Prompt Injection",
        objective="Test prompt injection",
        requested_tool_action=tool_action_data,
        parameters={},
        priority="high",
        reasoning="Test reasoning"
    )

    # Create scan config
    scan_config = ScanConfig(
        target=Target(url="http://example.com", scheme="http", host="example.com", port=80, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    # Execute the plan
    results = executor.execute(plan, scan_config)

    # Should return one failed result due to budget exceeded
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_id == "action123"
    assert "Scan budget exceeded" in results[0].status


def test_execute_malformed_url():
    """Test execution with malformed URL"""
    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)

    # Create a mock tool
    mock_tool = MockHTTPTool()
    mock_registry.get_tool.return_value = mock_tool

    # Initialize executor
    executor = AgentExecutorImpl(mock_registry)

    # Create a test plan with malformed URL
    tool_action_data = {
        "action_id": "action123",
        "tool_name": "http_request",
        "arguments": {"url": "not-a-url", "method": "GET"},
        "target": "not-a-url",
        "safety_constraints": {}
    }

    plan = TestPlan(
        test_id="test123",
        target="http://example.com",
        vulnerability_category="Prompt Injection",
        objective="Test prompt injection",
        requested_tool_action=tool_action_data,
        parameters={},
        priority="high",
        reasoning="Test reasoning"
    )

    # Create scan config
    scan_config = ScanConfig(
        target=Target(url="http://example.com", scheme="http", host="example.com", port=80, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    # Execute the plan
    results = executor.execute(plan, scan_config)

    # Should return one failed result due to malformed URL
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].action_id == "action123"
    assert "Scope violation" in results[0].status


if __name__ == "__main__":
    pytest.main([__file__])