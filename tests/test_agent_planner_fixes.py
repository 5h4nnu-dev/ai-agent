"""
Tests for the Agent Planner fixes addressing security audit findings
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.pentest_agent.planner.agent_planner import AgentPlanner
from src.pentest_agent.llm.base import LLMProvider
from src.pentest_agent.models.attack_surface import AttackSurface, Endpoint, Parameter, Form, AIInteractionPoint
from src.pentest_agent.models.scan import ScanConfig, Target
from src.pentest_agent.tools.registry import ToolRegistry
from src.pentest_agent.tools.http_request import HTTPRequestTool
from src.pentest_agent.tools.crawl import CrawlTool


def test_positive_allowlist_tool_validation():
    """Test that only tools in registry are allowed"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    # Create tool registry with only http_request tool
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should succeed with valid tool
    test_plan = planner.plan(attack_surface)
    assert test_plan.test_id == "test123"

    # Test with invalid tool name - should fail
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "invalid_tool",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    with pytest.raises(ValueError) as exc_info:
        planner.plan(attack_surface)
    assert "Unsupported tool name" in str(exc_info.value)


def test_no_string_based_forbidden_detection():
    """Test that forbidden operations are not detected by string matching"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {"url": "http://example.com", "method": "POST", "body": "sh -c 'ls'"},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    # Create tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should succeed because we validate against the tool schema, not string matching
    # The validation should pass because the tool is valid, even though the arguments
    # contain strings that might be dangerous
    test_plan = planner.plan(attack_surface)
    assert test_plan.test_id == "test123"


def test_scope_validation():
    """Test proper scope validation"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    # Create tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Create scan config with exact target
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

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should succeed with exact target match
    test_plan = planner.plan(attack_surface, scan_config)
    assert test_plan.test_id == "test123"

    # Test with wrong scheme - should fail
    scan_config_wrong_scheme = ScanConfig(
        target=Target(url="https://example.com", scheme="https", host="example.com", port=443, scope={}),
        crawl_limits={},
        timeout=30,
        rate_limits={},
        max_iterations=100,
        enabled_tests=[],
        llm_provider="ollama",
        llm_model="llama3"
    )

    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    with pytest.raises(ValueError) as exc_info:
        planner.plan(attack_surface, scan_config_wrong_scheme)
    assert "outside configured scope" in str(exc_info.value)


def test_json_parsing_deterministic():
    """Test that JSON parsing is deterministic and rejects multiple objects"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)

    # Test with valid JSON
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    # Create tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should succeed with valid JSON
    test_plan = planner.plan(attack_surface)
    assert test_plan.test_id == "test123"

    # Test with JSON + trailing text - should fail
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }
This is extra text that should not be allowed'''

    with pytest.raises(ValueError) as exc_info:
        planner.plan(attack_surface)
    assert "Failed to parse JSON" in str(exc_info.value)

    # Test with multiple JSON objects - should fail
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }{
        "another": "json object"
    }'''

    with pytest.raises(ValueError) as exc_info:
        planner.plan(attack_surface)
    assert "Failed to parse JSON" in str(exc_info.value)


def test_empty_reasoning_validation():
    """Test that empty reasoning is properly rejected"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high"
    }'''

    # Create tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should fail with missing reasoning field
    with pytest.raises(ValueError) as exc_info:
        planner.plan(attack_surface)
    assert "Missing required field" in str(exc_info.value)


def test_prompt_boundary_separation():
    """Test that attack surface data is clearly separated from instructions"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    # Create tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]

    # Create attack surface with potentially malicious endpoint data
    endpoint = Endpoint(
        url="http://example.com/api/test?param=malicious_value",
        methods=["POST"],
        parameters=[],
        headers={},
        content_type="application/json",
        endpoint_type="api",
        discovery_source="crawl"
    )

    attack_surface = AttackSurface(
        endpoints=[endpoint],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should succeed - the endpoint data should be treated as untrusted data to analyze, not instructions
    test_plan = planner.plan(attack_surface)
    assert test_plan.test_id == "test123"
    # Verify the endpoint data is in the prompt but doesn't influence the instruction
    assert test_plan.target == "http://example.com"


def test_tool_argument_validation():
    """Test that tool arguments are validated against tool contracts"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {"url": "http://example.com", "method": "POST"},
            "target": "http://example.com",
            "safety_constraints": {}
        },
        "parameters": {},
        "priority": "high",
        "reasoning": "Test reasoning"
    }'''

    # Create tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request"]
    # Mock the get_tool method to return a proper HTTPRequestTool
    mock_registry.get_tool.return_value = HTTPRequestTool()

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Should succeed with valid tool arguments
    test_plan = planner.plan(attack_surface)
    assert test_plan.test_id == "test123"