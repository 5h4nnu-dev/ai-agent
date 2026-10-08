"""
Test target model validation
"""
import pytest
from src.pentest_agent.models.target import Target


def test_target_creation():
    """Test target model creation"""
    target = Target(
        url="https://example.com",
        scheme="https",
        host="example.com",
        port=443,
        scope={"allowed_domains": "example.com"}
    )
    assert target.url == "https://example.com"
    assert target.scheme == "https"
    assert target.host == "example.com"
    assert target.port == 443


def test_target_validation():
    """Test target model validation"""
    # This should work without validation errors
    target = Target(
        url="https://example.com",
        scheme="https",
        host="example.com",
        port=443,
        scope={"allowed_domains": "example.com"}
    )
    assert target is not None


if __name__ == "__main__":
    pytest.main([__file__])