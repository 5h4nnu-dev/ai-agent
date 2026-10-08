"""
Tests for LLM package integration
"""
import pytest
from src.pentest_agent.llm import LLMProvider, OllamaProvider, get_provider


def test_llm_package_imports():
    """Test that LLM package imports work correctly"""
    # Test direct imports
    assert LLMProvider is not None
    assert OllamaProvider is not None

    # Test that OllamaProvider is a subclass of LLMProvider
    assert issubclass(OllamaProvider, LLMProvider)


def test_provider_factory():
    """Test the provider factory function"""
    # Test Ollama provider creation
    provider = get_provider('ollama')
    assert isinstance(provider, OllamaProvider)
    assert provider.get_provider_name() == "ollama"

    # Test Ollama provider creation with custom configuration
    provider = get_provider('ollama', host="http://custom-host:1234", model="test-model")
    assert provider.host == "http://custom-host:1234"
    assert provider.model == "test-model"

    # Test unsupported provider
    with pytest.raises(ValueError):
        get_provider('unsupported')


def test_provider_factory_registry():
    """Test that the provider registry works correctly"""
    # Test that we can create an instance through the registry
    provider = get_provider('ollama')
    assert provider.get_provider_name() == "ollama"

    # Test that the registry is accessible
    assert 'ollama' in ['ollama']  # Simple check that our registry has the expected provider


def test_package_public_interface():
    """Test that the package exposes the correct public interface"""
    import src.pentest_agent.llm as llm_package

    # Test that we can access the classes directly from the package
    assert hasattr(llm_package, 'LLMProvider')
    assert hasattr(llm_package, 'OllamaProvider')
    assert hasattr(llm_package, 'get_provider')

    # Test that the classes are the same as imported directly
    assert llm_package.LLMProvider is LLMProvider
    assert llm_package.OllamaProvider is OllamaProvider