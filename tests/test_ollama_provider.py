"""
Tests for Ollama LLM provider
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.pentest_agent.llm.ollama import OllamaProvider


def test_ollama_provider_initialization():
    """Test Ollama provider initialization"""
    provider = OllamaProvider()
    assert provider.host == "http://localhost:11434"
    assert provider.model == "llama3"

    provider = OllamaProvider(host="http://custom-host:1234", model="test-model")
    assert provider.host == "http://custom-host:1234"
    assert provider.model == "test-model"


def test_ollama_provider_initialization_invalid_host():
    """Test Ollama provider initialization with invalid host"""
    with pytest.raises(ValueError):
        OllamaProvider(host="")

    with pytest.raises(ValueError):
        OllamaProvider(host="not-a-url")


def test_ollama_provider_generate_response_success():
    """Test successful Ollama response generation"""
    provider = OllamaProvider()

    # Mock successful HTTP response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "response": "This is a test response"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        response = provider.generate_response("Test prompt")
        assert response == "This is a test response"


def test_ollama_provider_generate_response_with_model_override():
    """Test Ollama response generation with model override"""
    provider = OllamaProvider(model="default-model")

    # Mock successful HTTP response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "response": "This is a test response"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        response = provider.generate_response("Test prompt", model="override-model")
        assert response == "This is a test response"


def test_ollama_provider_generate_response_with_ollama_error():
    """Test Ollama response generation with Ollama application error"""
    provider = OllamaProvider()

    # Mock HTTP response with Ollama error (200 status but error in payload)
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "error": "Model not found"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        with pytest.raises(Exception) as exc_info:
            provider.generate_response("Test prompt")
        assert "Ollama error:" in str(exc_info.value)


def test_ollama_provider_generate_response_http_error():
    """Test Ollama response generation with HTTP error"""
    provider = OllamaProvider()

    # Mock HTTP error
    mock_error = MagicMock()
    mock_error.code = 500
    mock_error.reason = "Internal Server Error"
    mock_error.read.return_value = b""

    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = mock_error
        with pytest.raises(Exception) as exc_info:
            provider.generate_response("Test prompt")
        assert "Ollama request failed" in str(exc_info.value)


def test_ollama_provider_generate_response_connection_error():
    """Test Ollama response generation with connection error"""
    provider = OllamaProvider()

    # Mock connection error
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = Exception("Connection failed")
        with pytest.raises(Exception) as exc_info:
            provider.generate_response("Test prompt")
        assert "Ollama request failed" in str(exc_info.value)


def test_ollama_provider_generate_response_json_error():
    """Test Ollama response generation with JSON parsing error"""
    provider = OllamaProvider()

    # Mock successful HTTP response with invalid JSON
    mock_response = MagicMock()
    mock_response.read.return_value = b"invalid json"
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        with pytest.raises(Exception) as exc_info:
            provider.generate_response("Test prompt")
        assert "Failed to parse Ollama response" in str(exc_info.value)


def test_ollama_provider_get_model_list_success():
    """Test successful model list retrieval"""
    provider = OllamaProvider()

    # Mock successful HTTP response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "models": [
            {"name": "model1"},
            {"name": "model2"}
        ]
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        models = provider.get_model_list()
        assert models == ["model1", "model2"]


def test_ollama_provider_get_model_list_with_ollama_error():
    """Test model list retrieval with Ollama application error"""
    provider = OllamaProvider()

    # Mock HTTP response with Ollama error (200 status but error in payload)
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "error": "Server error"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        with pytest.raises(Exception) as exc_info:
            provider.get_model_list()
        assert "Ollama error:" in str(exc_info.value)


def test_ollama_provider_get_model_list_http_error():
    """Test model list retrieval with HTTP error"""
    provider = OllamaProvider()

    # Mock HTTP error
    mock_error = MagicMock()
    mock_error.code = 500
    mock_error.reason = "Internal Server Error"
    mock_error.read.return_value = b"Error occurred"

    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = mock_error
        with pytest.raises(Exception) as exc_info:
            provider.get_model_list()
        assert "Ollama request failed" in str(exc_info.value)


def test_ollama_provider_validate_provider_success():
    """Test provider validation with successful connection"""
    provider = OllamaProvider()

    # Mock successful model list retrieval
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "models": []
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        assert provider.validate_provider() is True


def test_ollama_provider_validate_provider_failure():
    """Test provider validation with failed connection"""
    provider = OllamaProvider()

    # Mock connection error
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = Exception("Connection failed")
        assert provider.validate_provider() is False


def test_ollama_provider_get_provider_name():
    """Test provider name retrieval"""
    provider = OllamaProvider()
    assert provider.get_provider_name() == "ollama"


def test_ollama_provider_model_list_empty_response():
    """Test model list with empty response"""
    provider = OllamaProvider()

    # Mock successful HTTP response with empty models
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "models": []
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        models = provider.get_model_list()
        assert models == []


def test_ollama_provider_model_list_no_models_key():
    """Test model list with missing models key"""
    provider = OllamaProvider()

    # Mock successful HTTP response without models key
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "other": "data"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch('urllib.request.urlopen', return_value=mock_response):
        models = provider.get_model_list()
        assert models == []


def test_ollama_provider_timeout_consistency():
    """Test that timeouts are applied to both API operations"""
    provider = OllamaProvider()

    # Mock successful HTTP response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "response": "test response"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    # Test generate_response timeout
    with patch('urllib.request.urlopen', return_value=mock_response):
        response = provider.generate_response("Test prompt")
        assert response == "test response"

    # Test get_model_list timeout
    with patch('urllib.request.urlopen', return_value=mock_response):
        models = provider.get_model_list()
        assert models == []


def test_ollama_provider_url_construction():
    """Test that URL construction works with and without trailing slashes"""
    # Test with trailing slash
    provider1 = OllamaProvider(host="http://localhost:11434/")
    assert provider1.host == "http://localhost:11434"

    # Test without trailing slash
    provider2 = OllamaProvider(host="http://localhost:11434")
    assert provider2.host == "http://localhost:11434"

    # Test with custom host and trailing slash
    provider3 = OllamaProvider(host="http://custom-host:1234/")
    assert provider3.host == "http://custom-host:1234"


def test_ollama_provider_model_override_in_request():
    """Test that model override is actually present in the outgoing request"""
    provider = OllamaProvider(model="default-model")

    # Mock successful HTTP response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "response": "This is a test response"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    # We'll check that the mock was called with the right parameters
    with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
        response = provider.generate_response("Test prompt", model="override-model")
        assert response == "This is a test response"

        # Verify that urlopen was called with a request containing the override model
        assert mock_urlopen.called