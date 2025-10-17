import json
import logging
import time
from pathlib import Path
from threading import Lock
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
        request_interval: float = 1.0,
        responses_dir: Path | str = Path("responses"),
    ) -> None:
        self.api_client = api_client
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.request_interval = request_interval
        self._last_request_time = 0.0
        self._lock = Lock()
        self._client: Optional[object] = None
        self.responses_dir = Path(responses_dir)
        self._prepare_responses_dir()

        if self.api_client is None and self.api_key:
            self._initialize_client()
        elif self.api_client is None:
            self.api_client = DummyAPIClient()

    def _save_response(self, name: str, content: str) -> None:
        """Persist raw or validated LLM output to file."""
        path = self.responses_dir / name
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logger.debug("Saved response to %s", path)
        except OSError as e:
            logger.warning("Failed to write response %s: %s", path, e)

    def _prepare_responses_dir(self) -> None:
        """Create or clear the directory used for storing responses."""
        if self.responses_dir.exists():
            for f in self.responses_dir.iterdir():
                try:
                    if f.is_file():
                        f.unlink()
                    elif f.is_dir():
                        import shutil

                        shutil.rmtree(f)
                except OSError as e:
                    logger.warning("Failed to remove %s: %s", f, e)
        else:
            self.responses_dir.mkdir(parents=True, exist_ok=True)

    def _wait_for_slot(self) -> None:
        """Wait until enough time has passed since the last request."""
        with self._lock:
            now = time.time()
            wait = self._last_request_time + self.request_interval - now
            if wait > 0:
                time.sleep(wait)
            self._last_request_time = time.time()

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
        self._wait_for_slot()
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

    def query(self, prompt: str, name: str = "response") -> Dict[str, Any]:
        """Send prompt twice, store responses and verify matching JSON."""
        for attempt in range(2):
            logger.debug("LLM query attempt %d for %s", attempt + 1, name)
            res1 = self._send_prompt(prompt)
            self._save_response(f"{name}_attempt{attempt+1}_1.txt", res1)
            res2 = self._send_prompt(prompt)
            self._save_response(f"{name}_attempt{attempt+1}_2.txt", res2)
            try:
                j1 = json.loads(res1)
                j2 = json.loads(res2)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received for %s", name)
                continue
            if j1 == j2:
                logger.info("Received matching JSON responses for %s", name)
                self._save_response(
                    f"{name}_validated.json", json.dumps(j1, indent=2)
                )
                return j1
            logger.warning("Responses do not match for %s", name)
        logger.error("LLM validation failed for %s", name)
        raise LLMValidationError("Failed to obtain valid identical responses")

class DummyAPIClient:
    def send(self, prompt: str) -> str:
        """Mock API client for testing."""
        logger.debug("Dummy client received prompt: %s", prompt)
        return json.dumps({"prompt": prompt})
