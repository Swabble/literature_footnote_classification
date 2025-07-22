from pathlib import Path
import logging

from src.logging_manager import LoggingManager

from src import (
    load_literature_entries,
    load_footnotes,
    LLMClient,
    DummyAPIClient,
    StatusManager,
    Matcher,
)

if __name__ == "__main__":
    LoggingManager(Path("app.log"))
    logging.debug("Application started")
    entries = load_literature_entries(Path("data/literature.json"))
    footnotes = load_footnotes(Path("data/footnotes.html"))

    status = StatusManager(Path("status.json"))
    client = LLMClient(DummyAPIClient())
    matcher = Matcher(client, status)

    result = matcher.match(entries, footnotes)
    logging.info("Matching result: %s", result)
    print(result)
