from os import getcwd

import pytest

from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel
from notes_app.settings import Settings
from notes_app.utils.colors import Color, get_color_by_name, get_next_color_by_rgba
from notes_app.utils.file import SectionIdentifier, File
from notes_app.utils.fonts import get_next_font
from notes_app.utils.search import Search, DEFAULT_VALUE_SEARCH_CASE_SENSITIVE, DEFAULT_VALUE_SEARCH_ALL_SECTIONS
from notes_app.utils.time import format_epoch


@pytest.fixture()
def get_file():
    settings = Settings()

    controller = MyScreenController(
        settings=settings,
        model=MyScreenModel()
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
        assert get_next_color_by_rgba([1, 1, 1, 1]).name == "black"
        assert get_next_color_by_rgba([1, 1, 1, 1]).rgba_value == (0, 0, 0, 1)


class TestFont:
    def test_get_last_font(self):
        assert get_next_font("RobotoMono-Regular") == "DejaVuSans"


class TestTime:
    def test_format_epoch(self):
        assert format_epoch("%Y-%m-%d %H:%M:%S", 1650362948) == "2022-04-19 12:09:08"


class TestSearch:
    def test_search(self):
        search = Search()
        assert search.search_case_sensitive == DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
        assert search.search_all_sections == DEFAULT_VALUE_SEARCH_ALL_SECTIONS

    def test_search__case_insensitive(self):
        search = Search()
        assert search._case_insensitive_search(pattern="A", text="dacb") == [1]
        assert search._case_insensitive_search(pattern="a", text="dacb") == [1]

    def test_search__case_sensitive(self):
        search = Search()
        assert search._case_sensitive_search(pattern="A", text="dacb") == []
        assert search._case_sensitive_search(pattern="A", text="dACb") == [1]

    def test_search_for_occurrences(self, get_file):
        search = Search()

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="do", file=get_file, current_section_identifier=current_section_identifier
        ) == {'<section=first> ': [25]}


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
        assert raw_data == \
               """('<section=first> Quod equidem non reprehendo\n'\n '<section=second> Quis istum dolorem timet\n')"""

    def test__get_validated_raw_data(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert get_file._get_validated_raw_data(raw_data=raw_data) == "x"

    def test__get_section_identifiers_from_raw_data_content(self, get_file):
        assert get_file._get_section_identifiers_from_raw_data_content() == ["a", "b"]

    def test_default_section_identifier(self, get_file):
        assert get_file.default_section_identifier == "a"

    def test_section_identifiers(self, get_file):
        assert get_file.section_identifiers == ["a", "b"]

    def test_add_section_identifier(self, get_file):
        assert get_file.add_section_identifier(section_file_separator="<section=a> ") is None
        assert get_file.section_identifiers == []

    def test_delete_section_identifier(self, get_file):
        assert get_file.delete_section_identifier(section_file_separator="<section=a> ") is None
        assert get_file.section_identifiers == []

    def test_delete_all_section_identifiers(self, get_file):
        assert get_file.delete_all_section_identifiers() is None
        assert get_file.section_identifiers == []

    def test_set_get_section_content(self, get_file):
        assert get_file.set_section_content(section_file_separator="<section=a> ", section_content="some content") is None
        assert get_file.get_section_content(section_file_separator="<section=a> ") == "some content"

    def test_delete_section_content(self, get_file):
        assert get_file.delete_section_content(section_file_separator="<section=a> ") is None
        assert get_file.get_section_content(section_file_separator="<section=a> ") is None

    def test_delete_all_sections_content(self, get_file):
        assert get_file.delete_all_sections_content() is None
        assert get_file.transform_data_by_sections_to_raw_data_content() is None

    def test__transform_raw_data_content_to_data_by_sections(self, get_file):
        assert get_file._transform_raw_data_content_to_data_by_sections() is None

    def test_transform_data_by_sections_to_raw_data_content(self, get_file):
        assert get_file.transform_data_by_sections_to_raw_data_content() is None


