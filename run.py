from pathlib import Path

from src import (
    load_literature_entries,
    load_footnotes,
    LLMClient,
    DummyAPIClient,
    StatusManager,
    Matcher,
)

if __name__ == "__main__":
    entries = load_literature_entries(Path("data/literature.json"))
    footnotes = load_footnotes(Path("data/footnotes.html"))

    status = StatusManager(Path("status.json"))
    client = LLMClient(DummyAPIClient())
    matcher = Matcher(client, status)

    result = matcher.match(entries, footnotes)
    print(result)
