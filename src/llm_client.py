import json
from typing import Any, Dict

class LLMValidationError(Exception):
    pass


class LLMClient:
    def __init__(self, api_client):
        self.api_client = api_client

    def _send_prompt(self, prompt: str) -> str:
        """Send prompt using provided API client."""
        # This is a placeholder for real API call
        return self.api_client.send(prompt)

    def query(self, prompt: str) -> Dict[str, Any]:
        """Send prompt twice and verify matching JSON responses."""
        for attempt in range(2):
            res1 = self._send_prompt(prompt)
            res2 = self._send_prompt(prompt)
            try:
                j1 = json.loads(res1)
                j2 = json.loads(res2)
            except json.JSONDecodeError:
                continue
            if j1 == j2:
                return j1
        raise LLMValidationError("Failed to obtain valid identical responses")

class DummyAPIClient:
    def send(self, prompt: str) -> str:
        """Mock API client for testing."""
        return json.dumps({"prompt": prompt})
