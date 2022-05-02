from os import getcwd

import pytest

from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel, FALLBACK_NOTES_FILE_PATH
from notes_app.settings import Settings
from notes_app.utils.color import Color, get_color_by_name, get_next_color_by_rgba
from notes_app.utils.file import SectionIdentifier, File
from notes_app.utils.font import get_next_font
from notes_app.utils.mark import _get_marked, get_marked_search_result, \
    get_marked_selected_text_input
from notes_app.utils.search import Search, validate_search_input, \
    regex_search_function, full_words_search_function, SEARCH_MINIMAL_CHAR_COUNT, \
    DEFAULT_VALUE_SEARCH_CASE_SENSITIVE, DEFAULT_VALUE_SEARCH_ALL_SECTIONS, \
    DEFAULT_VALUE_SEARCH_FULL_WORDS
from notes_app.utils.time import format_epoch


@pytest.fixture()
def get_file():
    settings = Settings()

    controller = MyScreenController(
        settings=settings,
        model=MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
    )

    file = File(
        file_path=f"{getcwd()}/assets/sample.txt",
        controller=controller
    )
    return file


class TestColor:
    def test_color(self):
        assert Color("black", (0, 0, 0, 1))
        assert Color("white", (1, 1, 1, 1))

    def test_get_color_by_name(self):
        assert get_color_by_name("black").name == "black"
        assert get_color_by_name("black").rgba_value == (0, 0, 0, 1)
        assert get_color_by_name("white").name == "white"
        assert get_color_by_name("white").rgba_value == (1, 1, 1, 1)

    def test_get_last_color(self):
        assert get_next_color_by_rgba(rgba_value=[1, 1, 1, 1]).name == "black"
        assert get_next_color_by_rgba(rgba_value=[1, 1, 1, 1]).rgba_value == (0, 0, 0, 1)

        assert get_next_color_by_rgba(rgba_value=[1, 1, 1, 1], skip_rgba_value=[1, 1, 1, 1]).name == "black"
        assert get_next_color_by_rgba(rgba_value=[1, 1, 1, 1], skip_rgba_value=[1, 1, 1, 1]).rgba_value == (0, 0, 0, 1)

        assert get_next_color_by_rgba(rgba_value=[1, 1, 1, 1], skip_rgba_value=[0, 0, 0, 1]).name == "navy"
        assert get_next_color_by_rgba(rgba_value=[1, 1, 1, 1], skip_rgba_value=[0, 0, 0, 1]).rgba_value == (0, 0, 0.5, 1)

        assert get_next_color_by_rgba(rgba_value=[1, 1, 0, 1], skip_rgba_value=[1, 1, 1, 1]).name == "black"
        assert get_next_color_by_rgba(rgba_value=[1, 1, 0, 1], skip_rgba_value=[1, 1, 1, 1]).rgba_value == (0, 0, 0, 1)


class TestFont:
    def test_get_last_font(self):
        assert get_next_font("RobotoMono-Regular") == "DejaVuSans"


class TestTime:
    def test_format_epoch(self):
        assert format_epoch("%Y-%m-%d %H:%M:%S", 1650362948) == "2022-04-19 12:09:08"


class TestSearch:
    @pytest.mark.parametrize("input_string, is_valid", [
        ("  ", False),
        (None, False),
        ((SEARCH_MINIMAL_CHAR_COUNT - 1) * "a", False),
        (SEARCH_MINIMAL_CHAR_COUNT * "a", True),
    ])
    def test_validate_search_input(self, input_string, is_valid):
        assert validate_search_input(input_string) is is_valid

    @pytest.mark.parametrize("pattern, text, occurrences", [
        ("is","this is some section.yeah",[2, 5]),
        ("is some","this is some section.yeah",[5]),
        ("his","this is some section.yeah",[1]),
    ])
    def test_regex_search_function(self, pattern, text, occurrences):
        assert regex_search_function(pattern, text) == occurrences

    @pytest.mark.parametrize("pattern, text, occurrences", [
        ("is","is some section.yeah", [0]),
        ("is","is is some is section.yeah", [0, 3, 11]),
        ("is","this is some is section.yeah", [5, 13]),
        ("is","this is some section.yeah",[5]),
        ("is some","this is some section.yeah",[]),
        ("his","this is some section.yeah",[]),
    ])
    def test_full_words_search_function(self, pattern, text, occurrences):
        assert full_words_search_function(pattern, text) == occurrences

    def test_search(self):
        search = Search()
        assert search.search_case_sensitive == DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
        assert search.search_all_sections == DEFAULT_VALUE_SEARCH_ALL_SECTIONS
        assert search.search_full_words == DEFAULT_VALUE_SEARCH_FULL_WORDS

    def test_search_default(self, get_file):
        search = Search()

        search.search_case_sensitive = False
        search.search_all_sections = False
        search.search_full_words = False

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section_identifier=current_section_identifier
        ) == {'<section=first> ': [25]}

    def test_search_case_sensitive(self, get_file):
        search = Search()

        search.search_case_sensitive = True
        search.search_all_sections = False
        search.search_full_words = False

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section_identifier=current_section_identifier
        ) == {'<section=first> ': [25]}

        assert search.search_for_occurrences(
            pattern="dO", file=get_file, current_section_identifier=current_section_identifier
        ) == {}

    def test_search_all_sections(self, get_file):
        search = Search()

        search.search_case_sensitive = False
        search.search_all_sections = True
        search.search_full_words = False

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section_identifier=current_section_identifier
        ) == {'<section=first> ': [25], '<section=second> ': [11]}

    def test_search_full_words(self, get_file):
        search = Search()

        search.search_case_sensitive = False
        search.search_all_sections = False
        search.search_full_words = True

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="non", file=get_file, current_section_identifier=current_section_identifier
        ) == {'<section=first> ': [13]}

        assert search.search_for_occurrences(
            pattern="nonx", file=get_file, current_section_identifier=current_section_identifier
        ) == {}


class TestSectionIdentifier:
    def test_section_identifier(self):
        with pytest.raises(ValueError):
            SectionIdentifier()

        with pytest.raises(ValueError):
            SectionIdentifier(section_file_separator="", section_name="")

        assert SectionIdentifier(section_file_separator="<section=a> ").section_name == "a"
        assert SectionIdentifier(section_name="a").section_file_separator == "<section=a> "


class TestFile:
    def test_get_raw_data_content(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert raw_data == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""

    def test__get_validated_raw_data(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert get_file._get_validated_raw_data(raw_data=raw_data) == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""

    def test__get_section_identifiers_from_raw_data_content(self, get_file):
        assert all(
            [isinstance(x, SectionIdentifier) for x in
             get_file._get_section_identifiers_from_raw_data_content()]
        )

    def test_default_section_identifier(self, get_file):
        assert isinstance(get_file.default_section_identifier, SectionIdentifier)

    def test_section_identifiers(self, get_file):
        assert all(
            [isinstance(x, SectionIdentifier) for x in
             get_file.section_identifiers]
        )

    def test_add_section_identifier(self, get_file):
        assert get_file.add_section_identifier(section_file_separator="<section=a> ") is None
        assert len(get_file.section_identifiers) == 3
        assert all(
            [isinstance(x, SectionIdentifier) for x in
             get_file.section_identifiers]
        )

    def test_delete_section_identifier(self, get_file):
        assert get_file.delete_section_identifier(section_file_separator="<section=a> ") is None
        assert len(get_file.section_identifiers) == 2
        assert all(
            [isinstance(x, SectionIdentifier) for x in
             get_file.section_identifiers]
        )

    def test_delete_all_section_identifiers(self, get_file):
        assert get_file.delete_all_section_identifiers() is None
        assert get_file.section_identifiers == []

    def test_set_get_section_content(self, get_file):
        assert not get_file.set_section_content(section_file_separator="<section=a> ", section_content="some content")
        assert get_file.get_section_content(section_file_separator="<section=a> ") == "some content"

    def test_delete_section_content(self, get_file):
        get_file.set_section_content(section_file_separator="<section=a> ", section_content="some content")
        assert not get_file.delete_section_content(section_file_separator="<section=a> ")
        with pytest.raises(KeyError):
            get_file.get_section_content(section_file_separator="<section=a> ")

    def test_delete_all_sections_content(self, get_file):
        assert not get_file.delete_all_sections_content()
        assert not get_file.transform_data_by_sections_to_raw_data_content()

    def test__transform_raw_data_content_to_data_by_sections(self, get_file):
        assert get_file._transform_raw_data_content_to_data_by_sections() == \
               {'<section=first> ': 'Quod equidem non reprehendo\n', '<section=second> ': 'Quis istum dolorem timet\n'}

    def test_transform_data_by_sections_to_raw_data_content(self, get_file):
        assert get_file.transform_data_by_sections_to_raw_data_content() == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""


class TestMark:
    def test__get_marked(self):
        assert _get_marked(
            input="some string",
            highlight_style="style",
            highlight_color="eeeeee"
        ) == "[style][color=eeeeee]some string[/color][/style]"

    def test_get_marked_search_result(self):
        assert get_marked_search_result(
            found_string="some string"
        ) == "[b][color=ff0000]some string[/color][/b]"

    def test_get_marked_selected_text_input(self):
        assert get_marked_selected_text_input(
            selected_string="some string"
        ) == "[i][color=ffaa00]some string[/color][/i]"
