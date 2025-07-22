import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class LLMValidationError(Exception):
    pass


class LLMClient:
    """Client for interacting with an OpenAI compatible LLM."""

    def __init__(
        self,
        api_client: Optional[object] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-4.1-nano",
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> None:
        self.api_client = api_client
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client: Optional[object] = None

        if self.api_client is None and self.api_key:
            self._initialize_client()
        elif self.api_client is None:
            self.api_client = DummyAPIClient()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai

            self._client = openai.OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized with model %s", self.model)
        except ImportError:
            logger.error(
                "OpenAI package not installed. Install with: pip install openai"
            )
            raise
        except Exception as e:
            logger.error("Failed to initialize OpenAI client: %s", e)
            raise

    def _send_prompt(self, prompt: str) -> str:
        """Send prompt using either the OpenAI client or the provided API client."""
        if self._client is not None:
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error("OpenAI API call failed: %s", e)
                raise
        logger.debug("Sending prompt to API: %s", prompt)
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
