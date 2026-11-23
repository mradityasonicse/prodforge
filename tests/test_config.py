"""Test suite for ProdForge configuration manager."""

import os
from prodforge.config import ProdForgeConfig, get_config


def test_default_config():
    cfg = get_config()
    assert cfg is not None
    assert cfg.ollama_host == "http://localhost:11434"
    assert cfg.studio_port == 8000
    assert cfg.studio_host == "127.0.0.1"


def test_provider_detection_offline():
    cfg = ProdForgeConfig(
        gemini_api_key=None,
        openai_api_key=None,
        anthropic_api_key=None,
        groq_api_key=None,
        openrouter_api_key=None
    )
    assert cfg.detected_provider == "offline"
    assert cfg.active_model == "offline-heuristic-engine"


def test_provider_detection_gemini():
    cfg = ProdForgeConfig(gemini_api_key="AIzaSyMockKey")
    assert cfg.detected_provider == "gemini"
    assert "gemini" in cfg.active_model


def test_provider_detection_openai():
    cfg = ProdForgeConfig(gemini_api_key=None, openai_api_key="sk-mockOpenAIKey")
    assert cfg.detected_provider == "openai"
    assert "gpt" in cfg.active_model


def test_model_override():
    cfg = ProdForgeConfig(gemini_api_key="AIzaMock", model_override="custom-claude-3")
    assert cfg.active_model == "custom-claude-3"
