from __future__ import annotations

import json
import urllib.request


class OpenAICompatibleProvider:
    """Provider-neutral adapter for OpenAI-compatible chat endpoints."""

    def __init__(self, endpoint: str, api_key: str, model: str, timeout: int = 30) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        request = urllib.request.Request(
            f"{self.endpoint}/chat/completions",
            data=json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0}).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode())
        return str(payload["choices"][0]["message"]["content"])
