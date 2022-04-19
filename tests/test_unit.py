import pytest

from notes_app.utils.colors import Color, get_color_by_name, get_next_color_by_rgba
from notes_app.utils.fonts import get_next_font
from notes_app.utils.time import format_epoch
from notes_app.utils.search import Search, DEFAULT_VALUE_SEARCH_CASE_SENSITIVE, DEFAULT_VALUE_SEARCH_ALL_SECTIONS
from notes_app.utils.file import SectionIdentifier, File


def test_color():
    assert Color("black", (0, 0, 0, 1))
    assert Color("white", (1, 1, 1, 1))


def test_get_color_by_name():
    assert get_color_by_name("black").name == "black"
    assert get_color_by_name("black").rgba_value == (0, 0, 0, 1)
    assert get_color_by_name("white").name == "white"
    assert get_color_by_name("white").rgba_value == (1, 1, 1, 1)


def test_get_last_color():
    assert get_next_color_by_rgba([1, 1, 1, 1]).name == "black"
    assert get_next_color_by_rgba([1, 1, 1, 1]).rgba_value == (0, 0, 0, 1)


def test_get_last_font():
    assert get_next_font("RobotoMono-Regular") == "DejaVuSans"


def test_format_epoch():
    assert format_epoch("%Y-%m-%d %H:%M:%S", 1650362948) == "2022-04-19 12:09:08"


def test_search():
    search = Search()
    assert search.search_case_sensitive == DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
    assert search.search_all_sections == DEFAULT_VALUE_SEARCH_ALL_SECTIONS


def test_search__case_insensitive():
    search = Search()
    assert search._case_insensitive_search(pattern="A", text="dacb") == [1]
    assert search._case_insensitive_search(pattern="a", text="dacb") == [1]


def test_search__case_sensitive():
    search = Search()
    assert search._case_sensitive_search(pattern="A", text="dacb") == []
    assert search._case_sensitive_search(pattern="A", text="dACb") == [1]


# TODO
def test_search_for_occurrences():
    search = Search()
    assert search.search_for_occurrences(pattern="A", file="", current_section_identifier="")


def test_section_identifier():
    with pytest.raises(ValueError):
        SectionIdentifier()

    with pytest.raises(ValueError):
        SectionIdentifier(section_file_separator="", section_name="")

    assert SectionIdentifier(section_file_separator="<section=a> ").section_name == "a"
    assert SectionIdentifier(section_name="a").section_file_separator == "<section=a> "


# TODO
def test_file():
    assert File(file_path="", controller="")

