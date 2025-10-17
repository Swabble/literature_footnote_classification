import logging
from pathlib import Path
from collections import defaultdict
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
        disamb_path = Path("prompt_templates/disambiguation_prompt.txt")
        self.disamb_prompt = disamb_path.read_text(encoding="utf-8").strip()

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
        result = self._resolve_duplicates(result, entries, footnotes)
        logger.info("Finished matching")
        return result

    def _build_prompt(self, entry: LiteratureEntry, footnotes: List[Footnote]) -> str:
        notes = "\n".join(f"{f.key}: {f.text}" for f in footnotes)
        prompt = "".join(
            (
                f"{self.base_prompt}\n\n",
                "Literature entry:\n",
                f"Key:{entry.key} ",
                f"FirstName:{entry.author_first} ",
                f"LastName:{entry.author_last} ",
                f"Year:{entry.year}\n",
                f"Footnotes:\n{notes}",
            )
        )
        logger.debug("Built prompt for entry %s: %s", entry.key, prompt)
        return prompt

    def _build_disambiguation_prompt(
        self, footnote: Footnote, entries: List[LiteratureEntry]
    ) -> str:
        options = "\n".join(
            "".join(
                (
                    "Literature entry:\n",
                    f"Key:{e.key} ",
                    f"FirstName:{e.author_first} ",
                    f"LastName:{e.author_last} ",
                    f"Year:{e.year}\n",
                )
            )
            for e in entries
        )
        prompt = "".join(
            (
                f"{self.disamb_prompt}\n\n",
                f"Footnote:\n{footnote.key} {footnote.text}\n",
                f"Entries:\n{options}",
            )
        )
        logger.debug(
            "Built disambiguation prompt for footnote %s: %s", footnote.key, prompt
        )
        return prompt

    def _resolve_duplicates(
        self,
        matches: Dict[str, List[str]],
        entries: List[LiteratureEntry],
        footnotes: List[Footnote],
    ) -> Dict[str, List[str]]:
        entry_lookup = {e.key: e for e in entries}
        footnote_lookup = {f.key: f for f in footnotes}

        occurrences: Dict[str, List[str]] = defaultdict(list)
        for entry_key, note_keys in matches.items():
            for fkey in note_keys:
                occurrences[fkey].append(entry_key)

        duplicates = {fk: ekeys for fk, ekeys in occurrences.items() if len(ekeys) > 1}

        for fkey, ekeys in duplicates.items():
            footnote = footnote_lookup.get(fkey)
            if not footnote:
                continue
            candidate_entries = [entry_lookup[k] for k in ekeys if k in entry_lookup]
            prompt = self._build_disambiguation_prompt(footnote, candidate_entries)
            name = f"{fkey}_disamb"

            try:
                response = self.llm_client.query(prompt, name=name)
                chosen = response.get(fkey)
            except Exception as e:
                logger.error("Disambiguation query failed: %s", e)
                chosen = None

            if not chosen or chosen not in ekeys:
                if chosen and chosen not in ekeys:
                    logger.warning(
                        "LLM returned invalid entry %s for footnote %s", chosen, fkey
                    )
                # remove footnote from all entries if disambiguation fails
                for ekey in ekeys:
                    if fkey in matches.get(ekey, []):
                        matches[ekey].remove(fkey)
                continue

            for ekey in ekeys:
                if ekey != chosen and fkey in matches.get(ekey, []):
                    matches[ekey].remove(fkey)
        return matches
