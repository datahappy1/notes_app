import re
from dataclasses import dataclass, asdict
from typing import List

from notes_app.domain.drawing import Drawing
from notes_app.services.search_service import (
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


@dataclass
class Section:
    text: str


@dataclass
class Note:
    section: Section
    text: str


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

    @staticmethod
    def transform_section_separator_to_section_name(
        defaults, section_separator: str
    ) -> str:
        return re.search(
            defaults.DEFAULT_SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX,
            section_separator,
        ).group(1)

    @staticmethod
    def transform_section_name_to_section_separator(
        defaults,
        section_name: str,
    ) -> str:
        return defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(name=section_name)

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

            section_name = self.transform_section_separator_to_section_name(
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
                        preview=text[position : end + preview_length],
                    )
                )

        return results

    def search_all_sections_simple(self, query: str) -> List[SearchResult]:
        return self.search(
            query=query,
            current_section=self.get_section_by_name(self.list_sections()[0].text).text,
            case_sensitive=False,
            full_words=False,
            all_sections=True,
        )

    def get_section(self, section_separator: str) -> Section:
        text = self.file.get_section_content(section_separator)

        return Section(Drawing.remove_from_text(text))

    def get_section_by_name(self, section_name: str) -> Section:
        separator = self.transform_section_name_to_section_separator(
            defaults=self.defaults,
            section_name=section_name,
        )

        text = self.file.get_section_content(separator)

        return Section(Drawing.remove_from_text(text))

    def list_sections(self) -> List[Section]:
        return [
            Section(
                self.transform_section_separator_to_section_name(
                    defaults=self.defaults,
                    section_separator=s,
                )
            )
            for s in self.file.section_separators_sorted
        ]

    def save_section(self, section_separator: str, text: str):
        if section_separator in self.file.section_separators_sorted:
            existing_text = self.file.get_section_content(section_separator)

            drawing = Drawing.from_text(existing_text)

            text = Drawing.replace_in_text(
                text,
                drawing,
            )

        self.file.set_section_content(
            section_separator=section_separator,
            section_content=text,
        )

    def save_section_by_name(self, section_name: str, text: str):
        separator = self.transform_section_name_to_section_separator(
            defaults=self.defaults,
            section_name=section_name,
        )

        if separator in self.file.section_separators_sorted:
            existing_text = self.file.get_section_content(separator)

            drawing = Drawing.from_text(existing_text)

            text = Drawing.replace_in_text(
                text,
                drawing,
            )

        self.file.set_section_content(
            section_separator=separator,
            section_content=text,
        )

    def create_section(self, section_separator: str, text: str = ""):
        self.file.set_section_content(
            section_separator=section_separator,
            section_content=text,
        )

    def create_section_by_name(self, section_name: str, text: str = ""):
        separator = self.transform_section_name_to_section_separator(
            defaults=self.defaults,
            section_name=section_name,
        )

        self.file.set_section_content(
            section_separator=separator,
            section_content=text,
        )

    def delete_section(self, section_separator: str):
        self.file.delete_section_content(section_separator)

    def delete_section_by_name(self, section_name: str):
        separator = self.transform_section_name_to_section_separator(
            defaults=self.defaults,
            section_name=section_name,
        )

        self.file.delete_section_content(separator)

    def rename_section(
        self,
        old_section_separator: str,
        new_section_separator: str,
    ):
        self.file.rename_section(
            old_section_separator=old_section_separator,
            new_section_separator=new_section_separator,
        )

    def rename_section_by_name(
        self,
        old_section_name: str,
        new_section_name: str,
    ):
        old_section_separator = self.transform_section_name_to_section_separator(
            defaults=self.defaults,
            section_name=old_section_name,
        )

        new_section_separator = self.transform_section_name_to_section_separator(
            defaults=self.defaults,
            section_name=new_section_name,
        )

        self.file.rename_section(
            old_section_separator=old_section_separator,
            new_section_separator=new_section_separator,
        )

    def update_file(self, file):
        self.file = file
