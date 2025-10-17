import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class LiteratureEntry:
    segment_id: str
    title: str
    author_first: str
    author_last: str
    doi: str
    url: str
    year: int
    key: str = field(default="")

@dataclass
class Footnote:
    footnote_id: str
    text: str
    key: str = field(default="")


def load_literature_entries(path: Path) -> List[LiteratureEntry]:
    logger.debug("Loading literature entries from %s", path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    entries = []
    for i, item in enumerate(data, start=1):
        key = f"L{i:05d}"
        entries.append(
            LiteratureEntry(
                segment_id=item.get("segment_id"),
                title=item.get("titel"),
                author_first=item.get("autor", {}).get("vorname"),
                author_last=item.get("autor", {}).get("nachname"),
                doi=item.get("doi"),
                url=item.get("url"),
                year=item.get("erscheinungsjahr"),
                key=key,
            )
        )
        logger.debug("Loaded literature entry %s", key)
    logger.info("Loaded %d literature entries", len(entries))
    return entries


def load_footnotes(path: Path) -> List[Footnote]:
    logger.debug("Loading footnotes from %s", path)
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    footnotes = []
    for i, div in enumerate(soup.find_all("div"), start=1):
        footnote_id = div.get("id")
        if not footnote_id:
            continue
        key = f"F{i:05d}"
        text = div.get_text(strip=True)
        if not text:
            logger.debug("Skipping footnote %s with empty text", footnote_id)
            continue
        footnotes.append(
            Footnote(
                footnote_id=footnote_id,
                text=text,
                key=key,
            )
        )
        logger.debug("Loaded footnote %s", key)
    logger.info("Loaded %d footnotes", len(footnotes))
    return footnotes
