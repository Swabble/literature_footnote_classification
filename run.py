from pathlib import Path
import logging

from src import (
    load_literature_entries,
    load_footnotes,
    LLMClient,
    DummyAPIClient,
    StatusManager,
    Matcher,
)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(),
        ],
    )
    logging.debug("Application started")
    entries = load_literature_entries(Path("data/literature.json"))
    footnotes = load_footnotes(Path("data/footnotes.html"))

    status = StatusManager(Path("status.json"))
    client = LLMClient(DummyAPIClient())
    matcher = Matcher(client, status)

    result = matcher.match(entries, footnotes)
    logging.info("Matching result: %s", result)
    print(result)
