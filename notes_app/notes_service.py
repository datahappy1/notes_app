from dataclasses import dataclass, asdict
from typing import List

from notes_app.file import (
    transform_section_separator_to_section_name,
)
from notes_app.search import (
    Search,
    validate_search_input,
)


@dataclass
class SearchResult:
    section: str
    position: int
    matched_text: str
    preview: str

    def to_dict(self):
        return asdict(self)


class NotesService:
    """
    Public API of the Notes application.

    This class is intentionally UI-agnostic so it can be used by:
      - Kivy UI
      - MCP server
      - CLI
      - REST API
      - tests
    """

    def __init__(self, file, defaults):
        self.file = file
        self.defaults = defaults
        self.search_engine = Search(defaults)

    def search(
        self,
        query: str,
        current_section: str,
        *,
        case_sensitive=False,
        full_words=False,
        all_sections=False,
        preview_length=30,
    ) -> List[SearchResult]:

        if not validate_search_input(query):
            return []

        self.search_engine.search_case_sensitive = case_sensitive
        self.search_engine.search_full_words = full_words
        self.search_engine.search_all_sections = all_sections

        occurrences = self.search_engine.search_for_occurrences(
            pattern=query,
            file=self.file,
            current_section=current_section,
        )

        results = []

        for section_separator, positions in occurrences.items():
            text = self.file.get_section_content(section_separator)

            section_name = transform_section_separator_to_section_name(
                defaults=self.defaults,
                section_separator=section_separator,
            )

            for position in positions:
                end = position + len(query)

                results.append(
                    SearchResult(
                        section=section_name,
                        position=position,
                        matched_text=text[position:end],
                        preview=text[position:end + preview_length],
                    )
                )

        return results

    def get_section(self, section_separator: str) -> str:
        return self.file.get_section_content(section_separator)

    def list_sections(self):
        return [
            transform_section_separator_to_section_name(
                defaults=self.defaults,
                section_separator=s,
            )
            for s in self.file.section_separators_sorted
        ]

    def save_section(self, section_separator: str, text: str):
        self.file.set_section_content(
            section_separator=section_separator,
            section_content=text,
        )

    def create_section(self, section_separator: str, text: str = ""):
        self.file.set_section_content(
            section_separator=section_separator,
            section_content=text,
        )

    def delete_section(self, section_separator: str):
        self.file.delete_section_content(section_separator)