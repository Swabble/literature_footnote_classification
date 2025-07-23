import logging
from pathlib import Path
from typing import Dict, List

from .data_ingestion import LiteratureEntry, Footnote
from .llm_client import LLMClient
from .status_manager import StatusManager

logger = logging.getLogger(__name__)


class Matcher:
    def __init__(self, llm_client: LLMClient, status: StatusManager):
        self.llm_client = llm_client
        self.status = status
        template_path = Path("prompt_templates/basic_prompt.txt")
        self.base_prompt = template_path.read_text(encoding="utf-8").strip()

    def match(self, entries: List[LiteratureEntry], footnotes: List[Footnote]) -> Dict[str, List[str]]:
        logger.info("Starting matching of %d entries", len(entries))
        result: Dict[str, List[str]] = {}
        for entry in entries:
            logger.debug("Processing entry %s", entry.key)
            self.status.update("current_entry", entry.key)
            for i in range(0, len(footnotes), 10):
                chunk = footnotes[i:i+10]
                logger.debug("Sending chunk %d-%d for entry %s", i, i + len(chunk) - 1, entry.key)
                prompt = self._build_prompt(entry, chunk)
                name = f"{entry.key}_chunk{i//10:03d}"
                try:
                    response = self.llm_client.query(prompt, name=name)
                except Exception as e:
                    logger.error("LLM query failed: %s", e)
                    self.status.update("error", str(e))
                    continue
                footnote_keys = response.get(entry.key, [])
                logger.debug("Received %d footnote keys", len(footnote_keys))
                result.setdefault(entry.key, []).extend(footnote_keys)
        logger.info("Finished matching")
        return result

    def _build_prompt(self, entry: LiteratureEntry, footnotes: List[Footnote]) -> str:
        notes = "\n".join(f"{f.key}: {f.text}" for f in footnotes)
        prompt = (
            f"{self.base_prompt}\n\n"
            f"Literature entry:\n{entry.key} {entry.author_first} {entry.author_last} {entry.year}\n"
            f"Footnotes:\n{notes}"
        )
        logger.debug("Built prompt for entry %s: %s", entry.key, prompt)
        return prompt
