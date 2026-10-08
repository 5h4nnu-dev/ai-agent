"""
Tests for the Agent Planner component
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.pentest_agent.planner.agent_planner import AgentPlanner
from src.pentest_agent.llm.base import LLMProvider
from src.pentest_agent.models.attack_surface import AttackSurface, Endpoint, Parameter, Form, AIInteractionPoint
from src.pentest_agent.models.scan import ScanConfig, Target
from src.pentest_agent.tools.registry import ToolRegistry
from src.pentest_agent.models.agent import TestPlan


def test_planner_initialization():
    """Test planner initialization"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '{"test_id": "test123", "target": "test", "vulnerability_category": "Prompt Injection", "objective": "Test prompt injection", "requested_tool_action": {"action_id": "action123", "tool_name": "http_request", "arguments": {}, "target": "http://example.com", "safety_constraints": {}}, "parameters": {}, "priority": "high", "reasoning": "Test reasoning"}'

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)
    assert planner.llm_provider == mock_llm
    assert planner.tool_registry == mock_registry


def test_planner_plan_success():
    """Test successful planning"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '''{
        "test_id": "test123",
        "target": "http://example.com",
        "vulnerability_category": "Prompt Injection",
        "objective": "Test prompt injection in AI endpoint",
        "requested_tool_action": {
            "action_id": "action123",
            "tool_name": "http_request",
            "arguments": {"url": "http://example.com/api", "method": "POST"},
            "target": "http://example.com/api",
            "safety_constraints": {"max_redirects": 3}
        },
        "parameters": {"prompt": "test prompt"},
        "priority": "high",
        "reasoning": "This is detailed reasoning for the test plan"
    }'''

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
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

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Plan should succeed
    test_plan = planner.plan(attack_surface, scan_config)
    assert test_plan.test_id == "test123"
    assert test_plan.vulnerability_category == "Prompt Injection"
    assert test_plan.priority == "high"
    assert test_plan.reasoning == "This is detailed reasoning for the test plan"


def test_planner_plan_malformed_response():
    """Test planning with malformed LLM response"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = "This is not valid JSON"

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

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

    # Planning should fail with ValueError
    with pytest.raises(ValueError):
        planner.plan(attack_surface)


def test_planner_plan_invalid_tool_name():
    """Test planning with invalid tool name in response"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
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

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

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

    # Planning should fail with ValueError due to invalid tool name
    with pytest.raises(ValueError):
        planner.plan(attack_surface)


def test_planner_plan_empty_response():
    """Test planning with empty LLM response"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = ""

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

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

    # Planning should fail with ValueError
    with pytest.raises(ValueError):
        planner.plan(attack_surface)


def test_planner_prompt_construction():
    """Test that prompt is constructed correctly"""
    # Create mock LLM provider
    mock_llm = Mock(spec=LLMProvider)
    mock_llm.generate_response.return_value = '{"test_id": "test123", "target": "test", "vulnerability_category": "Prompt Injection", "objective": "Test prompt injection", "requested_tool_action": {"action_id": "action123", "tool_name": "http_request", "arguments": {}, "target": "http://example.com", "safety_constraints": {}}, "parameters": {}, "priority": "high", "reasoning": "Test reasoning"}'

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

    # Create attack surface with data
    endpoint = Endpoint(
        url="http://example.com/api",
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

    # Construct prompt
    prompt = planner._construct_prompt(attack_surface)

    # Should contain expected elements
    assert "ATTACK SURFACE INFORMATION (UNTRUSTED DATA TO ANALYZE)" in prompt
    assert "Endpoints (1 total)" in prompt
    assert "http://example.com/api" in prompt
    assert "INSTRUCTIONS" in prompt
    assert "RESPONSE FORMAT" in prompt


def test_planner_plan_with_scan_config():
    """Test planning with scan configuration"""
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
        "reasoning": "Test reasoning for scan config"
    }'''

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

    # Create attack surface
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
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

    # Initialize planner
    planner = AgentPlanner(mock_llm, mock_registry)

    # Plan should succeed with scan config
    test_plan = planner.plan(attack_surface, scan_config)
    assert test_plan.test_id == "test123"


def test_planner_plan_with_empty_reasoning():
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

    # Create mock tool registry
    mock_registry = Mock(spec=ToolRegistry)
    mock_registry.list_tools.return_value = ["http_request", "crawl"]

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

    # Planning should fail with missing reasoning
    with pytest.raises(ValueError):
        planner.plan(attack_surface)