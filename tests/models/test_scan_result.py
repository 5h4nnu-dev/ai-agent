"""
Test scan result model validation
"""
import pytest
from src.pentest_agent.models.findings import ScanResult


def test_scan_result_creation():
    """Test scan result model creation"""
    scan_result = ScanResult(
        scan_metadata={"target": "https://example.com"},
        findings=[],
        limitations=[],
        statistics={"requests": "100"},
        completion_status="completed"
    )
    assert scan_result.completion_status == "completed"


def test_scan_result_validation():
    """Test scan result model validation"""
    # This should work without validation errors
    scan_result = ScanResult(
        scan_metadata={"target": "https://example.com"},
        findings=[],
        limitations=[],
        statistics={"requests": "100"},
        completion_status="completed"
    )
    assert scan_result is not None


def test_scan_result_invalid_status():
    """Test scan result model with invalid status"""
    with pytest.raises(Exception):
        ScanResult(
            scan_metadata={"target": "https://example.com"},
            findings=[],
            limitations=[],
            statistics={"requests": "100"},
            completion_status="invalid_status"
        )


if __name__ == "__main__":
    pytest.main([__file__])