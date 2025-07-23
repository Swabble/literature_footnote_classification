from pathlib import Path
import logging
import json

from src.logging_manager import LoggingManager

from src import (
    load_literature_entries,
    load_footnotes,
    LLMClient,
    StatusManager,
    Matcher,
)

if __name__ == "__main__":
    LoggingManager(Path("app.log"))
    logging.debug("Application started")

    # Load configuration
    config_path = Path("config.json")
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}

    entries = load_literature_entries(Path("data/literature.json"))
    footnotes = load_footnotes(Path("data/footnotes.html"))

    status = StatusManager(Path("status.json"))
    client = LLMClient(
        api_key=config.get("api_key"),
        model=config.get("model", "gpt-4.1-nano"),
        max_tokens=config.get("max_tokens", 500),
        temperature=config.get("temperature", 0.3),
        request_interval=config.get("request_interval", 1.0),
        responses_dir=Path(config.get("responses_dir", "responses")),
    )
    matcher = Matcher(client, status)

    result = matcher.match(entries, footnotes)
    logging.info("Matching result: %s", result)
    print(result)
