import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class LLMValidationError(Exception):
    pass


class LLMClient:
    def __init__(self, api_client):
        self.api_client = api_client

    def _send_prompt(self, prompt: str) -> str:
        """Send prompt using provided API client."""
        logger.debug("Sending prompt to API: %s", prompt)
        # This is a placeholder for real API call
        response = self.api_client.send(prompt)
        logger.debug("Received response: %s", response)
        return response

    def query(self, prompt: str) -> Dict[str, Any]:
        """Send prompt twice and verify matching JSON responses.""" 
        for attempt in range(2):
            logger.debug("LLM query attempt %d", attempt + 1)
            res1 = self._send_prompt(prompt)
            res2 = self._send_prompt(prompt)
            try:
                j1 = json.loads(res1)
                j2 = json.loads(res2)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received")
                continue
            if j1 == j2:
                logger.info("Received matching JSON responses")
                return j1
            logger.warning("Responses do not match")
        logger.error("LLM validation failed")
        raise LLMValidationError("Failed to obtain valid identical responses")

class DummyAPIClient:
    def send(self, prompt: str) -> str:
        """Mock API client for testing."""
        logger.debug("Dummy client received prompt: %s", prompt)
        return json.dumps({"prompt": prompt})
