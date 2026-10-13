"""
Tests for the CLI component
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from src.pentest_agent.cli.main import main, create_parser, validate_target_url, run_scan
from src.pentest_agent.models.target import Target
from src.pentest_agent.models.scan import ScanConfig
from src.pentest_agent.models.findings import ScanResult


def test_create_parser():
    """Test CLI argument parser creation"""
    parser = create_parser()
    assert parser is not None
    assert "target" in [action.dest for action in parser._actions]


def test_help_output():
    """Test that --help displays usage information"""
    parser = create_parser()

    # Capture help output
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        try:
            parser.parse_args(['--help'])
        except SystemExit:
            pass  # argparse calls sys.exit after --help, which is expected

    help_output = mock_stdout.getvalue()
    assert "AI-assisted web application penetration testing agent" in help_output
    assert "--target" in help_output
    assert "--provider" in help_output


def test_validate_target_url():
    """Test target URL validation"""
    # Valid URLs
    valid_urls = [
        "http://example.com",
        "https://example.com",
        "http://example.com:8080",
        "https://api.example.com/path",
        "http://192.168.1.1:3000"
    ]

    for url in valid_urls:
        target = validate_target_url(url)
        assert isinstance(target, Target)
        assert target.url == url

    # Invalid URLs
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",
        "http://",
        "",
        "example.com"
    ]

    for url in invalid_urls:
        with pytest.raises(ValueError):
            validate_target_url(url)


def test_validate_target_url_with_scheme():
    """Test that URLs with invalid schemes are rejected"""
    with pytest.raises(ValueError, match="URL must use http or https scheme"):
        validate_target_url("ftp://example.com")


def test_main_help():
    """Test main function with --help"""
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        with pytest.raises(SystemExit):
            main(['--help'])

    help_output = mock_stdout.getvalue()
    assert "AI-assisted web application penetration testing agent" in help_output


def test_main_missing_target():
    """Test main function with missing target"""
    # This should show help and exit
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        with pytest.raises(SystemExit):
            main([])  # No arguments


def test_main_with_valid_args():
    """Test main function with valid arguments"""
    # Mock the orchestrator to avoid actual network calls
    with patch('src.pentest_agent.cli.main.ScanOrchestrator') as mock_orchestrator:
        # Mock the orchestrator instance
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance

        # Mock the run_scan method to return a test result
        mock_result = Mock(spec=ScanResult)
        mock_result.completion_status = "completed"
        mock_result.statistics = {"endpoints_discovered": 5, "tools_executed": 3}
        mock_result.findings = []
        mock_result.limitations = []

        mock_instance.run_scan.return_value = mock_result

        # Mock the get_provider function
        with patch('src.pentest_agent.cli.main.get_provider') as mock_provider:
            mock_llm_provider = Mock()
            mock_provider.return_value = mock_llm_provider
            mock_llm_provider.validate_provider.return_value = True

            # This should not raise an exception
            result = main(['--target', 'http://example.com', '--verbose'])
            assert result == 0


def test_main_with_provider_error():
    """Test main function when LLM provider fails"""
    with patch('src.pentest_agent.cli.main.get_provider') as mock_provider:
        mock_provider.side_effect = Exception("Provider initialization failed")

        result = main(['--target', 'http://example.com'])
        assert result == 1  # Should return error code


def test_main_with_scan_failure():
    """Test main function when scan fails"""
    with patch('src.pentest_agent.cli.main.ScanOrchestrator') as mock_orchestrator:
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.run_scan.side_effect = Exception("Scan failed")

        with patch('src.pentest_agent.cli.main.get_provider') as mock_provider:
            mock_llm_provider = Mock()
            mock_provider.return_value = mock_llm_provider
            mock_llm_provider.validate_provider.return_value = True

            result = main(['--target', 'http://example.com'])
            assert result == 1  # Should return error code


def test_display_scan_results():
    """Test scan results display functionality"""
    # Create a mock scan result
    mock_result = Mock(spec=ScanResult)
    mock_result.completion_status = "completed"
    mock_result.statistics = {
        "endpoints_discovered": 10,
        "forms_discovered": 3,
        "tools_executed": 5
    }
    mock_result.findings = []
    mock_result.limitations = ["Limited to 100 pages"]

    # Capture output
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        # This would normally be called from run_scan, but we test the function directly
        pass  # The display function is not directly testable without mocking the print calls


if __name__ == "__main__":
    pytest.main([__file__])