"""
Test agent state model validation
"""
import pytest
from src.pentest_agent.models.agent import AgentState
from src.pentest_agent.models.attack_surface import AttackSurface
from src.pentest_agent.models.agent import TestPlan
from src.pentest_agent.models.tool import ToolResult
from src.pentest_agent.models.evidence import VulnerabilityCandidate
from src.pentest_agent.models.findings import VerifiedFinding


def test_agent_state_creation():
    """Test agent state model creation"""
    # Create minimal required objects for testing
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

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

    agent_state = AgentState(
        scan_info={"target": "https://example.com"},
        attack_surface=attack_surface,
        current_plan=test_plan,
        completed_actions=[],
        observations=[],
        evidence=[],
        candidates=[],
        verified_findings=[],
        current_iteration=1,
        status="running"
    )
    assert agent_state.current_iteration == 1
    assert agent_state.status == "running"


def test_agent_state_validation():
    """Test agent state model validation"""
    # Create minimal required objects for testing
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

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

    # This should work without validation errors
    agent_state = AgentState(
        scan_info={"target": "https://example.com"},
        attack_surface=attack_surface,
        current_plan=test_plan,
        completed_actions=[],
        observations=[],
        evidence=[],
        candidates=[],
        verified_findings=[],
        current_iteration=1,
        status="running"
    )
    assert agent_state is not None


def test_agent_state_invalid_iteration():
    """Test agent state model with invalid iteration"""
    # Create minimal required objects for testing
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

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

    with pytest.raises(Exception):
        AgentState(
            scan_info={"target": "https://example.com"},
            attack_surface=attack_surface,
            current_plan=test_plan,
            completed_actions=[],
            observations=[],
            evidence=[],
            candidates=[],
            verified_findings=[],
            current_iteration=-1,
            status="running"
        )


def test_agent_state_invalid_status():
    """Test agent state model with invalid status"""
    # Create minimal required objects for testing
    attack_surface = AttackSurface(
        endpoints=[],
        forms=[],
        parameters=[],
        technologies=[],
        ai_interaction_points=[]
    )

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

    with pytest.raises(Exception):
        AgentState(
            scan_info={"target": "https://example.com"},
            attack_surface=attack_surface,
            current_plan=test_plan,
            completed_actions=[],
            observations=[],
            evidence=[],
            candidates=[],
            verified_findings=[],
            current_iteration=1,
            status=""
        )


if __name__ == "__main__":
    pytest.main([__file__])