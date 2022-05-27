import uuid

import pytest

from notes_app.utils.color import (
    Color,
    get_color_by_name,
    get_next_color_by_rgba,
    AVAILABLE_COLORS,
)
from notes_app.utils.default_notes_file import DefaultNotesFile, DEFAULT_NOTES_FILE_CONTENT, DEFAULT_NOTES_FILE_NAME
from notes_app.utils.file import SectionIdentifier, File
from notes_app.utils.font import get_next_font, AVAILABLE_FONTS
from notes_app.utils.mark import _get_marked, get_marked_search_result
from notes_app.utils.search import (
    Search,
    validate_search_input,
    regex_search_function,
    full_words_search_function,
    SEARCH_MINIMAL_CHAR_COUNT,
    DEFAULT_VALUE_SEARCH_CASE_SENSITIVE,
    DEFAULT_VALUE_SEARCH_ALL_SECTIONS,
    DEFAULT_VALUE_SEARCH_FULL_WORDS,
    transform_position_text_placeholder_to_position,
    transform_position_to_position_text_placeholder,
    transform_section_name_to_section_text_placeholder,
    transform_section_text_placeholder_to_section_name,
)
from notes_app.utils.time import format_epoch
from tests.conftest import (
    delete_default_notes_file,
    read_default_notes_file,
    read_settings_file,
    TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH,
    TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH,
    create_default_notes_file,
    TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT,
    TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME,
)


class TestColor:
    def test_color(self):
        assert Color("black", (0, 0, 0, 1))
        assert Color("white", (1, 1, 1, 1))

    def test_get_color_by_name(self):
        assert (
                get_color_by_name(colors_list=AVAILABLE_COLORS, color_name="black").name
                == "black"
        )
        assert get_color_by_name(
            colors_list=AVAILABLE_COLORS, color_name="black"
        ).rgba_value == (0, 0, 0, 1)
        assert (
                get_color_by_name(colors_list=AVAILABLE_COLORS, color_name="white").name
                == "white"
        )
        assert get_color_by_name(
            colors_list=AVAILABLE_COLORS, color_name="white"
        ).rgba_value == (1, 1, 1, 1)

    def test_get_last_color(self):
        assert (
                get_next_color_by_rgba(
                    colors_list=AVAILABLE_COLORS, rgba_value=[1, 1, 1, 1]
                ).name
                == "black"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS, rgba_value=[1, 1, 1, 1]
        ).rgba_value == (0, 0, 0, 1,)

        assert (
                get_next_color_by_rgba(
                    colors_list=AVAILABLE_COLORS,
                    rgba_value=[1, 1, 1, 1],
                    skip_rgba_value=[1, 1, 1, 1],
                ).name
                == "black"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS,
            rgba_value=[1, 1, 1, 1],
            skip_rgba_value=[1, 1, 1, 1],
        ).rgba_value == (0, 0, 0, 1)

        assert (
                get_next_color_by_rgba(
                    colors_list=AVAILABLE_COLORS,
                    rgba_value=[1, 1, 1, 1],
                    skip_rgba_value=[0, 0, 0, 1],
                ).name
                == "navy"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS,
            rgba_value=[1, 1, 1, 1],
            skip_rgba_value=[0, 0, 0, 1],
        ).rgba_value == (0, 0, 0.5, 1)

        assert (
                get_next_color_by_rgba(
                    colors_list=AVAILABLE_COLORS,
                    rgba_value=[1, 1, 0, 1],
                    skip_rgba_value=[1, 1, 1, 1],
                ).name
                == "black"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS,
            rgba_value=[1, 1, 0, 1],
            skip_rgba_value=[1, 1, 1, 1],
        ).rgba_value == (0, 0, 0, 1)


class TestFont:
    def test_get_last_font(self):
        assert (
                get_next_font(fonts_list=AVAILABLE_FONTS, font_name="RobotoMono-Regular")
                == "DejaVuSans"
        )


class TestTime:
    def test_format_epoch(self):
        assert format_epoch("%Y-%m-%d %H:%M:%S", 1650362948) == "2022-04-19 12:09:08"


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
        "pattern, text, occurrences",
        [
            ("is", "this is some section.yeah", [2, 5]),
            ("is some", "this is some section.yeah", [5]),
            ("his", "this is some section.yeah", [1]),
        ],
    )
    def test_regex_search_function(self, pattern, text, occurrences):
        assert regex_search_function(pattern, text) == occurrences

    @pytest.mark.parametrize(
        "pattern, text, occurrences",
        [
            ("is", "is some section.yeah", [0]),
            ("is", "is is some is section.yeah", [0, 3, 11]),
            ("is", "this is some is section.yeah", [5, 13]),
            ("is", "this is some section.yeah", [5]),
            ("is some", "this is some section.yeah", []),
            ("his", "this is some section.yeah", []),
        ],
    )
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
            pattern="do",
            file=get_file,
            current_section_identifier=current_section_identifier,
        ) == {"<section=first> ": [25]}

    def test_search_case_sensitive(self, get_file):
        search = Search()

        search.search_case_sensitive = True
        search.search_all_sections = False
        search.search_full_words = False

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="do",
            file=get_file,
            current_section_identifier=current_section_identifier,
        ) == {"<section=first> ": [25]}

        assert (
                search.search_for_occurrences(
                    pattern="dO",
                    file=get_file,
                    current_section_identifier=current_section_identifier,
                )
                == {}
        )

    def test_search_all_sections(self, get_file):
        search = Search()

        search.search_case_sensitive = False
        search.search_all_sections = True
        search.search_full_words = False

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="do",
            file=get_file,
            current_section_identifier=current_section_identifier,
        ) == {"<section=first> ": [25], "<section=second> ": [11]}

    def test_search_full_words(self, get_file):
        search = Search()

        search.search_case_sensitive = False
        search.search_all_sections = False
        search.search_full_words = True

        current_section_identifier = SectionIdentifier(
            section_file_separator="<section=first> "
        )

        assert search.search_for_occurrences(
            pattern="non",
            file=get_file,
            current_section_identifier=current_section_identifier,
        ) == {"<section=first> ": [13]}

        assert (
                search.search_for_occurrences(
                    pattern="nonx",
                    file=get_file,
                    current_section_identifier=current_section_identifier,
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


class TestSectionIdentifier:
    def test_section_identifier(self):
        with pytest.raises(ValueError):
            SectionIdentifier()

        with pytest.raises(ValueError):
            SectionIdentifier(section_file_separator="", section_name="")

        assert (
                SectionIdentifier(section_file_separator="<section=a> ").section_name == "a"
        )
        assert (
                SectionIdentifier(section_name="a").section_file_separator == "<section=a> "
        )


class TestFile:
    def test_get_validated_file_path(self):
        create_default_notes_file()
        file_path = TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH
        assert File.get_validated_file_path(file_path=file_path) == file_path
        # results in FileNotFoundError
        file_path = f"{TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH}/sample_not_existing_{uuid.uuid4().hex}.txt"
        assert File.get_validated_file_path(file_path=file_path) is None
        # results in PermissionError
        file_path = TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH
        assert File.get_validated_file_path(file_path=file_path) is None

    def test_get_raw_data_content(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert (
                raw_data
                == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test__get_validated_raw_data(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert (
                get_file._get_validated_raw_data(raw_data=raw_data)
                == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test__get_section_identifiers_from_raw_data_content(self, get_file):
        assert all(
            [
                isinstance(x, SectionIdentifier)
                for x in get_file._get_section_identifiers_from_raw_data_content()
            ]
        )

    def test_default_section_identifier(self, get_file):
        assert isinstance(get_file.default_section_identifier, SectionIdentifier)

    def test_section_identifiers(self, get_file):
        assert all(
            [isinstance(x, SectionIdentifier) for x in get_file.section_identifiers]
        )

    def test_add_section_identifier(self, get_file):
        assert (
                get_file.add_section_identifier(section_file_separator="<section=a> ")
                is None
        )
        assert len(get_file.section_identifiers) == 3
        assert all(
            [isinstance(x, SectionIdentifier) for x in get_file.section_identifiers]
        )

    def test_delete_section_identifier(self, get_file):
        assert (
                get_file.delete_section_identifier(section_file_separator="<section=a> ")
                is None
        )
        assert len(get_file.section_identifiers) == 2
        assert all(
            [isinstance(x, SectionIdentifier) for x in get_file.section_identifiers]
        )

    def test_delete_all_section_identifiers(self, get_file):
        assert get_file.delete_all_section_identifiers() is None
        assert get_file.section_identifiers == []

    def test_set_get_section_content(self, get_file):
        assert not get_file.set_section_content(
            section_file_separator="<section=a> ", section_content="some content"
        )
        assert (
                get_file.get_section_content(section_file_separator="<section=a> ")
                == "some content"
        )

    def test_delete_section_content(self, get_file):
        get_file.set_section_content(
            section_file_separator="<section=a> ", section_content="some content"
        )
        assert not get_file.delete_section_content(
            section_file_separator="<section=a> "
        )
        with pytest.raises(KeyError):
            get_file.get_section_content(section_file_separator="<section=a> ")

    def test_delete_all_sections_content(self, get_file):
        assert not get_file.delete_all_sections_content()
        assert not get_file.transform_data_by_sections_to_raw_data_content()

    def test__transform_raw_data_content_to_data_by_sections(self, get_file):
        assert get_file._transform_raw_data_content_to_data_by_sections() == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }

    def test_transform_data_by_sections_to_raw_data_content(self, get_file):
        assert (
                get_file.transform_data_by_sections_to_raw_data_content()
                == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )


class TestDefaultFile:
    def teardown_method(self, test_method):
        delete_default_notes_file()

    def test_default_file(self):
        default_notes_file = DefaultNotesFile()
        assert default_notes_file.default_notes_file_name == DEFAULT_NOTES_FILE_NAME
        assert default_notes_file.default_notes_file_content == DEFAULT_NOTES_FILE_CONTENT

    def test_generate_default_file(self):
        DefaultNotesFile(
            notes_file_name=TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME,
            notes_file_content=TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT,
        ).generate_default_file()
        assert read_default_notes_file() == TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT


class TestSettings:
    def test__set_missing_store_defaults(self, get_settings):
        get_settings.store.font_name = None
        get_settings.store.font_size = None
        get_settings.store.background_color = None
        get_settings.store.foreground_color = None

        get_settings._set_missing_store_defaults()

        json_data = read_settings_file()

        assert json_data["font_name"] == {"value": "Roboto-Bold"}
        assert json_data["font_size"] == {"value": "14.0"}
        assert json_data["background_color"] == {"value": "blue"}
        assert json_data["foreground_color"] == {"value": "green"}

    def test_set_get_font_name(self, get_settings):
        get_settings.font_name = "Roboto"
        assert get_settings.font_name == "Roboto"

    def test_set_get_font_size(self, get_settings):
        get_settings.font_size = "20"
        assert get_settings.font_size == "20"

    def test_set_get_background_color(self, get_settings):
        get_settings.background_color = "red"
        assert get_settings.background_color == "red"

    def test_set_get_foreground_color(self, get_settings):
        get_settings.foreground_color = "yellow"
        assert get_settings.foreground_color == "yellow"

    def test_dump(self, get_settings):
        get_settings.font_name = "arial"
        get_settings.font_size = "50.0"
        get_settings.background_color = "blue"
        get_settings.foreground_color = "olive"
        assert get_settings.dump() is None

        json_data = read_settings_file()

        assert json_data["font_name"] == {"value": "arial"}
        assert json_data["font_size"] == {"value": "50.0"}
        assert json_data["background_color"] == {"value": "blue"}
        assert json_data["foreground_color"] == {"value": "olive"}


class TestMark:
    def test__get_marked(self):
        assert (
                _get_marked(
                    string="some string",
                    highlight_style="some_style",
                    highlight_color="some_color",
                )
                == "[some_style][color=some_color]some string[/color][/some_style]"
        )

    def test_get_marked_search_result(self):
        assert (
                get_marked_search_result(found_string="some string")
                == "[b][color=ff0000]some string[/color][/b]"
        )
