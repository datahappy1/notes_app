import re
from typing import AnyStr

SEARCH_MINIMAL_CHAR_COUNT = 2

DEFAULT_VALUE_SEARCH_CASE_SENSITIVE = False
DEFAULT_VALUE_SEARCH_ALL_SECTIONS = False
DEFAULT_VALUE_SEARCH_FULL_WORDS = False

SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT = 30
SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE = "section "
SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE = "position "


def validate_search_input(input_string):
    if (
        not input_string
        or len(input_string) < SEARCH_MINIMAL_CHAR_COUNT
        or input_string.isspace()
    ):
        return False
    return True


def regex_search_function(pattern, text):
    return [m.start() for m in re.finditer(pattern, text)]


def full_words_search_function(pattern, text):
    words_split = text.split(" ")

    def _get_position(i):
        return len(" ".join(words_split[0:i]))

    return [
        _get_position(i) + 1 if i > 0 else _get_position(i)
        for i, word in enumerate(words_split)
        if word == pattern
    ]


class Search:
    def __init__(self):
        self._search_case_sensitive = DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
        self._search_all_sections = DEFAULT_VALUE_SEARCH_ALL_SECTIONS
        self._search_full_words = DEFAULT_VALUE_SEARCH_FULL_WORDS

    @property
    def search_case_sensitive(self):
        return self._search_case_sensitive

    @search_case_sensitive.setter
    def search_case_sensitive(self, value):
        self._search_case_sensitive = value

    @property
    def search_all_sections(self):
        return self._search_all_sections

    @search_all_sections.setter
    def search_all_sections(self, value):
        self._search_all_sections = value

    @property
    def search_full_words(self):
        return self._search_full_words

    @search_full_words.setter
    def search_full_words(self, value):
        self._search_full_words = value

    def search_for_occurrences(self, pattern, file, current_section_identifier):
        found_occurrences = dict()

        if self.search_full_words:
            search_function = full_words_search_function
        else:
            search_function = regex_search_function

        if self.search_all_sections:
            sections_to_search_in = file.section_identifiers
        else:
            sections_to_search_in = [current_section_identifier]

        for section in sections_to_search_in:
            text = file.get_section_content(
                section_file_separator=section.section_file_separator
            )

            if self.search_case_sensitive:
                pass
            else:
                pattern = pattern.lower()
                text = text.lower()

            search_result = search_function(pattern=pattern, text=text)
            if search_result:
                found_occurrences[section.section_file_separator] = search_result

        return found_occurrences


def transform_position_text_placeholder_to_position(
    position_text_placeholder: AnyStr = None,
) -> int:
    if position_text_placeholder:
        return int(
            position_text_placeholder.replace(
                SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE, ""
            )
        )
    return 0


def transform_position_to_position_text_placeholder(position_start: int = 0) -> AnyStr:
    if position_start:
        return f"{SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE}{position_start}"
    return f"{SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE}{0}"


def transform_section_text_placeholder_to_section_name(
    section_text_placeholder: AnyStr = None,
) -> AnyStr:
    if section_text_placeholder:
        return section_text_placeholder.replace(
            SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE, ""
        )
    return ""


def transform_section_name_to_section_text_placeholder(
    section_name: AnyStr = "",
) -> AnyStr:
    if section_name:
        return f"{SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE}{section_name}"
    return f"{SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE}"
