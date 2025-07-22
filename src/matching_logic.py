from typing import Dict, List

from .data_ingestion import LiteratureEntry, Footnote
from .llm_client import LLMClient
from .status_manager import StatusManager


class Matcher:
    def __init__(self, llm_client: LLMClient, status: StatusManager):
        self.llm_client = llm_client
        self.status = status

    def match(self, entries: List[LiteratureEntry], footnotes: List[Footnote]) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        for entry in entries:
            self.status.update("current_entry", entry.key)
            for i in range(0, len(footnotes), 10):
                chunk = footnotes[i:i+10]
                prompt = self._build_prompt(entry, chunk)
                try:
                    response = self.llm_client.query(prompt)
                except Exception as e:
                    self.status.update("error", str(e))
                    continue
                footnote_keys = response.get(entry.key, [])
                result.setdefault(entry.key, []).extend(footnote_keys)
        return result

    def _build_prompt(self, entry: LiteratureEntry, footnotes: List[Footnote]) -> str:
        notes = "\n".join(f"{f.key}: {f.text}" for f in footnotes)
        prompt = f"Entry: {entry.key} {entry.title}\nFootnotes:\n{notes}"
        return prompt
