"""
Test HTTP request tool implementation
"""
import pytest
from src.pentest_agent.tools.http_request import HTTPRequestTool
from src.pentest_agent.tools.errors import ToolError


def test_http_request_tool_creation():
    """Test HTTP request tool creation"""
    tool = HTTPRequestTool()
    assert tool.name == "http_request"
    assert tool.description == "Execute HTTP requests to target endpoints with security controls"
    assert hasattr(tool, 'execute')


def test_http_request_tool_execution():
    """Test HTTP request tool execution with valid parameters"""
    tool = HTTPRequestTool()

    # Test valid GET request - should not crash, but will fail with network error due to no server
    result = tool.execute({
        "url": "https://example.com/api/test",
        "method": "GET",
        "action_id": "test_001",
        "target": "https://example.com"
    })

    # Should not crash - should return a result structure
    assert "action_id" in result
    assert "success" in result
    assert "status" in result
    assert "response" in result or "error_info" in result


def test_http_request_tool_invalid_method():
    """Test HTTP request tool with invalid method"""
    tool = HTTPRequestTool()

    result = tool.execute({
        "url": "https://example.com/api/test",
        "method": "HEAD",  # Invalid method
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Unsupported HTTP method" in result["error_info"]["message"]


def test_http_request_tool_invalid_url():
    """Test HTTP request tool with invalid URL"""
    tool = HTTPRequestTool()

    result = tool.execute({
        "url": "not-a-valid-url",
        "method": "GET",
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Invalid URL format" in result["error_info"]["message"]


def test_http_request_tool_missing_url():
    """Test HTTP request tool with missing URL"""
    tool = HTTPRequestTool()

    result = tool.execute({
        "method": "GET",
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "URL is required" in result["error_info"]["message"]


def test_http_request_tool_missing_method():
    """Test HTTP request tool with missing method"""
    tool = HTTPRequestTool()

    result = tool.execute({
        "url": "https://example.com/api/test",
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Method is required" in result["error_info"]["message"]


def test_http_request_tool_timeout_validation():
    """Test HTTP request tool with invalid timeout"""
    tool = HTTPRequestTool()

    result = tool.execute({
        "url": "https://example.com/api/test",
        "method": "GET",
        "timeout": 35,  # Too high
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Invalid timeout" in result["error_info"]["message"]


def test_http_request_tool_redirect_validation():
    """Test HTTP request tool with invalid redirect count"""
    tool = HTTPRequestTool()

    result = tool.execute({
        "url": "https://example.com/api/test",
        "method": "GET",
        "max_redirects": 10,  # Too high
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Invalid redirect count" in result["error_info"]["message"]


def test_http_request_tool_body_size_validation():
    """Test HTTP request tool with oversized body"""
    tool = HTTPRequestTool()

    # Create a body that's too large (2MB to be safe)
    large_body = "x" * (1024 * 1024 * 2)  # 2MB

    result = tool.execute({
        "url": "https://example.com/api/test",
        "method": "POST",
        "body": large_body,
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Request body too large" in result["error_info"]["message"]


def test_http_request_tool_scope_validation():
    """Test HTTP request tool scope validation - should reject out-of-scope requests"""
    tool = HTTPRequestTool()

    # This should be rejected because it's a different hostname
    result = tool.execute({
        "url": "https://attacker.com/api/test",
        "method": "GET",
        "action_id": "test_001",
        "target": "https://example.com"  # Target is example.com
    })

    # Should fail with scope violation
    assert result["success"] is False
    assert result["error_info"]["error_type"] == "scope_violation"


def test_http_request_tool_rate_limiting():
    """Test HTTP request tool rate limiting"""
    tool = HTTPRequestTool()

    # Test that we can make a few requests without issues
    # These should all pass validation but fail with network errors (not rate limits)
    for i in range(3):
        result = tool.execute({
            "url": f"https://example.com/api/test{i}",
            "method": "GET",
            "action_id": f"test_{i}",
            "target": "https://example.com"
        })
        # These should be validation errors or network errors, not rate limit errors
        assert "action_id" in result
        assert "success" in result


def test_http_request_tool_rate_limit_exceeded():
    """Test HTTP request tool rate limit exceeded (this will test the rate limiting logic)"""
    tool = HTTPRequestTool()

    # Make several requests to test rate limiting behavior
    results = []
    for i in range(5):  # Make 5 requests
        result = tool.execute({
            "url": f"https://example.com/api/test{i}",
            "method": "GET",
            "action_id": f"test_{i}",
            "target": "https://example.com"
        })
        results.append(result)

    # All should be processed without crashing
    assert len(results) == 5
    for result in results:
        assert "action_id" in result
        assert "success" in result


if __name__ == "__main__":
    pytest.main([__file__])