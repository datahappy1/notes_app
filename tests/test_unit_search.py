import pytest

from notes_app.defaults import Defaults
from notes_app.search import (
    SEARCH_MINIMAL_CHAR_COUNT,
    validate_search_input,
    _basic_search_function,
    _full_words_search_function,
    search_function,
    Search,
    transform_position_text_placeholder_to_position,
    transform_position_to_position_text_placeholder,
    transform_section_text_placeholder_to_section_name,
    transform_section_name_to_section_text_placeholder,
)

defaults = Defaults()


class TestSearch:
    @pytest.mark.parametrize(
        "input_string, is_valid",
        [
            ("  ", False),
            (None, False),
            ((SEARCH_MINIMAL_CHAR_COUNT - 1) * "a", False),
            (SEARCH_MINIMAL_CHAR_COUNT * "a", True),
        ],
    )
    def test_validate_search_input(self, input_string, is_valid):
        assert validate_search_input(input_string) is is_valid

    @pytest.mark.parametrize(
        "pattern, text, case_sensitive,occurrences",
        [
            ("is", "this is some section.yeah", False, [2, 5]),
            ("is some", "this is some section.yeah", False, [5]),
            ("his", "this is some section.yeah", False, [1]),
            ("is", "this is some section.yeah", True, [2, 5]),
            ("is Some", "this is Some section.yeah", True, [5]),
            ("hIs", "this is some section.yeah", True, []),
        ],
    )
    def test__basic_search_function(self, pattern, text, case_sensitive, occurrences):
        assert _basic_search_function(pattern, text, case_sensitive) == occurrences

    @pytest.mark.parametrize(
        "pattern, text, case_sensitive, occurrences",
        [
            ("is", "this is some section.yeah", False, [5]),
            ("is some", "this is some section.yeah", False, [5]),
            ("his", "this is some section.yeah", False, []),
            ("is", "this is some is section.yeah", True, [5, 13]),
            ("is Some", "this is Some section.yeah", True, [5]),
            ("hIs", "this is some section.yeah", True, []),
        ],
    )
    def test__full_words_search_function(
        self, pattern, text, case_sensitive, occurrences
    ):
        assert _full_words_search_function(pattern, text, case_sensitive) == occurrences

    @pytest.mark.parametrize(
        "pattern, text, case_sensitive, full_words_search, occurrences",
        [
            ("is", "this is some section.yeah", False, True, [5]),
            ("is some", "this is some section.yeah", False, True, [5]),
            ("his", "this is some section.yeah", False, True, []),
            ("is", "this is some section.yeah", True, True, [5]),
            ("is Some", "this is Some section.yeah", True, True, [5]),
            ("hIs", "this is some section.yeah", True, True, []),
            ("is", "this is some section.yeah", False, False, [2, 5]),
            ("is some", "this is some section.yeah", False, False, [5]),
            ("his", "this is some section.yeah", False, False, [1]),
            ("is", "this is some section.yeah", True, False, [2, 5]),
            ("is Some", "this is Some section.yeah", True, False, [5]),
            ("hIs", "this is some section.yeah", True, False, []),
        ],
    )
    def test_search_function(
        self, pattern, text, case_sensitive, full_words_search, occurrences
    ):
        assert (
            search_function(pattern, text, case_sensitive, full_words_search)
            == occurrences
        )

    def test_search(self):
        search = Search(defaults=defaults)
        assert (
            search.search_case_sensitive == defaults.DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
        )
        assert search.search_all_sections == defaults.DEFAULT_VALUE_SEARCH_ALL_SECTIONS
        assert search.search_full_words == defaults.DEFAULT_VALUE_SEARCH_FULL_WORDS

    def test_search_default(self, get_file):
        search = Search(defaults=defaults)

        search.search_case_sensitive = False
        search.search_all_sections = False
        search.search_full_words = False

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section="<section=first> ",
        ) == {"<section=first> ": [25]}

    def test_search_case_sensitive(self, get_file):
        search = Search(defaults=defaults)

        search.search_case_sensitive = True
        search.search_all_sections = False
        search.search_full_words = False

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section="<section=first> ",
        ) == {"<section=first> ": [25]}

        assert (
            search.search_for_occurrences(
                pattern="dO",
                file=get_file,
                current_section="<section=first> ",
            )
            == {}
        )

    def test_search_all_sections(self, get_file):
        search = Search(defaults=defaults)

        search.search_case_sensitive = False
        search.search_all_sections = True
        search.search_full_words = False

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section="<section=first> ",
        ) == {"<section=first> ": [25], "<section=second> ": [11]}

    def test_search_full_words(self, get_file):
        search = Search(defaults=defaults)

        search.search_case_sensitive = False
        search.search_all_sections = False
        search.search_full_words = True

        assert search.search_for_occurrences(
            pattern="non", file=get_file, current_section="<section=first> ",
        ) == {"<section=first> ": [13]}

        assert (
            search.search_for_occurrences(
                pattern="nonx",
                file=get_file,
                current_section="<section=first> ",
            )
            == {}
        )

    def test_transform_position_text_placeholder_to_position(self):
        assert (
            transform_position_text_placeholder_to_position(
                position_text_placeholder="position 1"
            )
            == 1
        )
        assert (
            transform_position_text_placeholder_to_position(
                position_text_placeholder="position 0"
            )
            == 0
        )
        assert (
            transform_position_text_placeholder_to_position(
                position_text_placeholder=None
            )
            == 0
        )

    def test_transform_position_to_position_text_placeholder(self):
        assert (
            transform_position_to_position_text_placeholder(position_start=1)
            == "position 1"
        )
        assert transform_position_to_position_text_placeholder() == "position 0"
        assert (
            transform_position_to_position_text_placeholder(position_start=None)
            == "position 0"
        )

    def test_transform_section_text_placeholder_to_section_name(self):
        assert (
            transform_section_text_placeholder_to_section_name(
                section_text_placeholder="section A"
            )
            == "A"
        )
        assert (
            transform_section_text_placeholder_to_section_name(
                section_text_placeholder=None
            )
            == ""
        )

    def test_transform_section_name_to_section_text_placeholder(self):
        assert (
            transform_section_name_to_section_text_placeholder(section_name="A")
            == "section A"
        )
        assert transform_section_name_to_section_text_placeholder() == "section "
        assert (
            transform_section_name_to_section_text_placeholder(section_name=None)
            == "section "
        )
