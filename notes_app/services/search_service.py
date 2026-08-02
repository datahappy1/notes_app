import re

SEARCH_MINIMAL_CHAR_COUNT = 2

SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT = 30
SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE = "section "
SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE = "position "

SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR = "ff0000"
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE = "b"


def validate_search_input(input_string):
    if (
        not input_string
        or len(input_string) < SEARCH_MINIMAL_CHAR_COUNT
        or input_string.isspace()
    ):
        return False
    return True


def _basic_search_function(pattern, text, case_sensitive_search):
    if case_sensitive_search:
        pass
    else:
        pattern = pattern.lower()
        text = text.lower()
    return [m.start() for m in re.finditer(pattern, text)]


def _full_words_search_function(pattern, text, case_sensitive_search):
    pattern = r"\b" + pattern + r"\b"
    if case_sensitive_search:
        regex = re.compile(pattern)
    else:
        regex = re.compile(pattern, re.IGNORECASE)
    return [m.start() for m in regex.finditer(text)]


def search_function(pattern, text, case_sensitive_search, full_words_search):
    if full_words_search:
        return _full_words_search_function(
            pattern=pattern, text=text, case_sensitive_search=case_sensitive_search
        )
    return _basic_search_function(
        pattern=pattern, text=text, case_sensitive_search=case_sensitive_search
    )


class Search:
    def __init__(self, defaults):
        self._search_case_sensitive = defaults.DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
        self._search_all_sections = defaults.DEFAULT_VALUE_SEARCH_ALL_SECTIONS
        self._search_full_words = defaults.DEFAULT_VALUE_SEARCH_FULL_WORDS

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

    def search_for_occurrences(self, pattern, file, current_section):
        found_occurrences = dict()

        if self.search_all_sections:
            sections_separators_to_search_in = file.section_separators_sorted
        else:
            sections_separators_to_search_in = [current_section]

        for section_separator in sections_separators_to_search_in:
            text = file.get_section_content(section_separator=section_separator)

            search_result = search_function(
                pattern=pattern,
                text=text,
                case_sensitive_search=self.search_case_sensitive,
                full_words_search=self.search_full_words,
            )
            if search_result:
                found_occurrences[section_separator] = search_result

        return found_occurrences


def transform_position_text_placeholder_to_position(
    position_text_placeholder: str = None,
) -> int:
    if position_text_placeholder:
        return int(
            position_text_placeholder.replace(
                SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE, ""
            )
        )
    return 0


def transform_position_to_position_text_placeholder(position_start: int = 0) -> str:
    if position_start:
        return f"{SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE}{position_start}"
    return f"{SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE}0"


def transform_section_text_placeholder_to_section_name(
    section_text_placeholder: str = None,
) -> str:
    if section_text_placeholder:
        return section_text_placeholder.replace(
            SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE, ""
        )
    return ""


def transform_section_name_to_section_text_placeholder(section_name: str = "",) -> str:
    if section_name:
        return f"{SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE}{section_name}"
    return f"{SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE}"
