"""
Playbook loader: reads the Helix negotiation playbook from a local file
and provides per-clause-type section retrieval.

In production, this replaces SharePoint RAG for the initial build.
The full playbook (~3,500 tokens) is loaded in-context per D5 §5 recommendation.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .models import TaskUnitType
from .config import PLAYBOOK_PATH, PLAYBOOK_VERSION


class PlaybookLoader:
    """
    Loads and indexes the local playbook file.
    Sections are delimited by headers matching TaskUnitType values.
    """

    def __init__(
        self,
        playbook_path: Path = PLAYBOOK_PATH,
        version: str = PLAYBOOK_VERSION,
    ) -> None:
        self._path = playbook_path
        self._version = version
        self._sections: dict[TaskUnitType, str] = {}
        self._loaded = False

    @property
    def version(self) -> str:
        return self._version

    def load(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Playbook not found at {self._path}. "
                "Create agent_build/playbook/playbook_v3_4.md or update config.PLAYBOOK_PATH."
            )
        raw = self._path.read_text(encoding="utf-8")
        self._sections = _parse_playbook_sections(raw)
        self._loaded = True

    def get_section(self, clause_type: TaskUnitType) -> str:
        """Returns the playbook section for the given clause type."""
        if not self._loaded:
            self.load()
        section = self._sections.get(clause_type)
        if not section:
            return f"[No playbook content found for {clause_type.value} in {self._path.name}]"
        return section

    def get_full_context(self) -> str:
        """
        Returns all 7 sections as a single context block (~3,500 tokens).
        Suitable for loading into the system prompt or a cached context block.
        """
        if not self._loaded:
            self.load()
        parts = []
        for t in TaskUnitType:
            content = self._sections.get(t, "[No content]")
            parts.append(f"## {t.value}\n{content}")
        return "\n\n".join(parts)

    def section_citation(self, clause_type: TaskUnitType) -> str:
        """Returns an audit-friendly citation string for Ironclad logging."""
        return f"{clause_type.value} — {self._path.name} ({self._version})"


def _parse_playbook_sections(raw: str) -> dict[TaskUnitType, str]:
    """
    Parses playbook markdown into per-clause-type sections.
    Section boundaries: lines containing a TaskUnitType value or its space-separated form.
    """
    sections: dict[TaskUnitType, str] = {}
    current_type: Optional[TaskUnitType] = None
    current_lines: list[str] = []

    for line in raw.splitlines():
        matched = _match_section_header(line)
        if matched is not None:
            if current_type is not None:
                sections[current_type] = "\n".join(current_lines).strip()
            current_type = matched
            current_lines = []
        elif current_type is not None:
            current_lines.append(line)

    if current_type is not None:
        sections[current_type] = "\n".join(current_lines).strip()

    return sections


def _match_section_header(line: str) -> Optional[TaskUnitType]:
    """Checks if a line is a section header for one of the 7 clause types."""
    # Match markdown headings (# ## ### etc.) or plain lines
    line_clean = re.sub(r"^#+\s*", "", line).strip().upper()
    for t in TaskUnitType:
        if t.value in line_clean or t.value.replace("_", " ") in line_clean:
            return t
    return None
