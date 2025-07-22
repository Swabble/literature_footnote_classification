"""Footnote to literature entry matching package."""

from .data_ingestion import load_literature_entries, load_footnotes
from .llm_client import LLMClient, DummyAPIClient
from .status_manager import StatusManager
from .matching_logic import Matcher

__all__ = [
    "load_literature_entries",
    "load_footnotes",
    "LLMClient",
    "DummyAPIClient",
    "StatusManager",
    "Matcher",
]
