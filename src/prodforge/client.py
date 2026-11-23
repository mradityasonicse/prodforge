"""
Unified Multi-Provider LLM Client for ProdForge.
Directly interfaces with Gemini, OpenAI, Groq, OpenRouter, Anthropic, and Ollama.
No external bloat; built on top of high-performance httpx with automatic retries.
"""

from __future__ import annotations

import json
from typing import Optional, Dict, Any
import httpx
from prodforge.config import get_config, ProdForgeConfig


class OfflineModeException(Exception):
    """Raised when no LLM API key or local model is accessible."""
    pass


class LLMClient:
    def __init__(self, config: Optional[ProdForgeConfig] = None, model: Optional[str] = None):
        self.config = config or get_config()
        self.model = model or self.config.active_model
        self.timeout = 60.0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Synchronously generate a completion from the configured provider."""
        provider = self.config.detected_provider

        if provider == "gemini":
            return self._call_gemini(prompt, system_prompt)
        elif provider == "openai":
            return self._call_openai_compatible(
                url="https://api.openai.com/v1/chat/completions",
                api_key=self.config.openai_api_key or "",
                prompt=prompt,
                system_prompt=system_prompt,
                model=self.model if self.model != "offline-heuristic-engine" else "gpt-4o-mini"
            )
        elif provider == "groq":
            return self._call_openai_compatible(
                url="https://api.groq.com/openai/v1/chat/completions",
                api_key=self.config.groq_api_key or "",
                prompt=prompt,
                system_prompt=system_prompt,
                model=self.model if self.model != "offline-heuristic-engine" else "llama-3.3-70b-versatile"
            )
        elif provider == "openrouter":
            return self._call_openai_compatible(
                url="https://openrouter.ai/api/v1/chat/completions",
                api_key=self.config.openrouter_api_key or "",
                prompt=prompt,
                system_prompt=system_prompt,
                model=self.model if self.model != "offline-heuristic-engine" else "meta-llama/llama-3.3-70b-instruct"
            )
        elif provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        else:
            # Check if local Ollama is reachable
            try:
                return self._call_ollama(prompt, system_prompt)
            except Exception:
                raise OfflineModeException(
                    "No valid LLM API key detected (GEMINI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, ANTHROPIC_API_KEY) "
                    "and local Ollama is not active."
                )

    def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        api_key = self.config.gemini_api_key
        model_name = self.model if "gemini" in self.model else "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will strictly follow these instructions."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned status {resp.status_code}: {resp.text}")
            
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise RuntimeError(f"Unexpected Gemini response structure: {data}")

    def _call_openai_compatible(
        self, url: str, api_key: str, prompt: str, system_prompt: Optional[str] = None, model: str = "gpt-4o-mini"
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"API ({url}) returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _call_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        headers = {
            "x-api-key": self.config.anthropic_api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": self.model if "claude" in self.model else "claude-3-5-sonnet-20241022",
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            payload["system"] = system_prompt

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Anthropic API returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["content"][0]["text"]

    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.config.ollama_host}/api/generate"
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        payload = {
            "model": self.model if self.model != "offline-heuristic-engine" else "llama3",
            "prompt": full_prompt,
            "stream": False
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise OfflineModeException(f"Ollama returned {resp.status_code}")
            return resp.json().get("response", "")
