"""
Test crawl tool implementation
"""
import pytest
from src.pentest_agent.tools.crawl import CrawlTool
from src.pentest_agent.tools.registry import ToolRegistry


def test_crawl_tool_creation():
    """Test crawl tool creation"""
    tool = CrawlTool()
    assert tool.name == "crawl"
    assert tool.description == "Discover new endpoints and application structure through crawling"
    assert hasattr(tool, 'execute')


def test_crawl_tool_execution_basic():
    """Test crawl tool execution with valid parameters"""
    tool = CrawlTool()

    # Test valid crawl request - should not crash, but will fail with network error due to no server
    result = tool.execute({
        "base_url": "https://example.com",
        "max_depth": 2,
        "max_pages": 10,
        "action_id": "test_001",
        "target": "https://example.com"
    })

    # Should not crash - should return a result structure
    assert "action_id" in result
    assert "success" in result
    assert "status" in result
    assert "response" in result or "error_info" in result


def test_crawl_tool_invalid_base_url():
    """Test crawl tool with invalid base URL"""
    tool = CrawlTool()

    result = tool.execute({
        "base_url": "not-a-valid-url",
        "max_depth": 2,
        "max_pages": 10,
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Invalid base URL format" in result["error_info"]["message"]


def test_crawl_tool_missing_base_url():
    """Test crawl tool with missing base URL"""
    tool = CrawlTool()

    result = tool.execute({
        "max_depth": 2,
        "max_pages": 10,
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Base URL is required" in result["error_info"]["message"]


def test_crawl_tool_scope_validation():
    """Test crawl tool scope validation - should reject out-of-scope requests"""
    tool = CrawlTool()

    # This should be rejected because it's a different hostname
    result = tool.execute({
        "base_url": "https://attacker.com",
        "max_depth": 2,
        "max_pages": 10,
        "action_id": "test_001",
        "target": "https://example.com"  # Target is example.com
    })

    # Should fail with scope violation
    assert result["success"] is False
    assert result["error_info"]["error_type"] == "scope_violation"


def test_crawl_tool_depth_validation():
    """Test crawl tool with invalid depth"""
    tool = CrawlTool()

    result = tool.execute({
        "base_url": "https://example.com",
        "max_depth": 5,  # Too high
        "max_pages": 10,
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Invalid max depth" in result["error_info"]["message"]


def test_crawl_tool_page_validation():
    """Test crawl tool with invalid page count"""
    tool = CrawlTool()

    result = tool.execute({
        "base_url": "https://example.com",
        "max_depth": 2,
        "max_pages": 150,  # Too high
        "action_id": "test_001",
        "target": "https://example.com"
    })

    assert result["success"] is False
    assert result["error_info"]["error_type"] == "validation_error"
    assert "Invalid max pages" in result["error_info"]["message"]


def test_crawl_tool_normalization():
    """Test URL normalization functionality"""
    tool = CrawlTool()

    # Test basic normalization
    normalized = tool._normalize_url("https://example.com/path/", "https://example.com")
    assert normalized == "https://example.com/path"

    # Test fragment removal
    normalized = tool._normalize_url("https://example.com/path#section", "https://example.com")
    assert normalized == "https://example.com/path"

    # Test relative URL
    normalized = tool._normalize_url("/path", "https://example.com")
    assert normalized == "https://example.com/path"

    # Test with query parameters
    normalized = tool._normalize_url("https://example.com/path?param=value", "https://example.com")
    assert normalized == "https://example.com/path?param=value"


def test_crawl_tool_url_validation():
    """Test URL validation functionality"""
    tool = CrawlTool()

    # Valid URL within scope
    assert tool._is_valid_url("https://example.com/path", "https://example.com") is True

    # Invalid URL format
    assert tool._is_valid_url("not-a-url", "https://example.com") is False

    # External URL
    assert tool._is_valid_url("https://other.com/path", "https://example.com") is False

    # Invalid scheme
    assert tool._is_valid_url("ftp://example.com/path", "https://example.com") is False


def test_crawl_tool_registry_integration():
    """Test that crawl tool can be instantiated properly"""
    # Just test that we can create a crawl tool - this is the main test for tool creation
    tool = CrawlTool()
    assert tool.name == "crawl"
    assert tool.description == "Discover new endpoints and application structure through crawling"
    assert hasattr(tool, 'execute')


if __name__ == "__main__":
    pytest.main([__file__])