"""
ProdForge Configuration Manager.
Handles multi-provider keys, local Ollama endpoints, and runtime defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Search for .env in current directory, user home, or repository root
load_dotenv(Path.cwd() / ".env")
load_dotenv(Path.home() / ".prodforge" / ".env")
if Path("D:/prodforge/.env").exists():
    load_dotenv(Path("D:/prodforge/.env"))

ProviderType = Literal["gemini", "openai", "anthropic", "groq", "openrouter", "ollama", "offline"]

class ProdForgeConfig(BaseModel):
    # API Keys
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    groq_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    openrouter_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    
    # Ollama endpoint
    ollama_host: str = Field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    
    # Default model override
    model_override: Optional[str] = Field(default_factory=lambda: os.getenv("PRODFORGE_MODEL"))
    
    # Studio Server Port
    studio_port: int = Field(default_factory=lambda: int(os.getenv("PRODFORGE_PORT", "8000")))
    studio_host: str = Field(default_factory=lambda: os.getenv("PRODFORGE_HOST", "127.0.0.1"))

    @property
    def detected_provider(self) -> ProviderType:
        if self.gemini_api_key:
            return "gemini"
        if self.openai_api_key:
            return "openai"
        if self.anthropic_api_key:
            return "anthropic"
        if self.groq_api_key:
            return "groq"
        if self.openrouter_api_key:
            return "openrouter"
        return "offline"

    @property
    def active_model(self) -> str:
        if self.model_override:
            return self.model_override
        
        provider = self.detected_provider
        if provider == "gemini":
            return "gemini-2.5-flash"
        if provider == "openai":
            return "gpt-4o-mini"
        if provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        if provider == "groq":
            return "llama-3.3-70b-versatile"
        if provider == "openrouter":
            return "meta-llama/llama-3.3-70b-instruct"
        if provider == "ollama":
            return "llama3"
        return "offline-heuristic-engine"


def get_config() -> ProdForgeConfig:
    """Retrieve the singleton configuration instance."""
    return ProdForgeConfig()
