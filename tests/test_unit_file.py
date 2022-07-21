import uuid

import pytest

from notes_app.defaults import Defaults
from notes_app.file import (
    get_validated_file_path,
    transform_section_separator_to_section_name,
    transform_section_name_to_section_separator,
)

defaults = Defaults()


def test_get_validated_file_path():
    file_path = defaults.DEFAULT_NOTES_FILE_NAME
    assert get_validated_file_path(file_path=file_path) == file_path

    file_path = f"sample_not_existing_{uuid.uuid4().hex}.txt"
    assert get_validated_file_path(file_path=file_path) is None


def test_transform_section_separator_to_section_name(get_file):
    assert (
        transform_section_separator_to_section_name(
            defaults=get_file.defaults, section_separator="<section=a> "
        )
        == "a"
    )


def test_transform_section_name_to_section_separator(get_file):
    assert (
        transform_section_name_to_section_separator(
            defaults=get_file.defaults, section_name="a"
        )
        == "<section=a> "
    )


class TestFile:
    def test__get_validated_raw_data(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert (
            get_file._get_validated_raw_data(raw_data=raw_data)
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test_reload(self, get_file):
        get_file.set_section_content(
            section_separator="<section=third>", section_content="test"
        )
        assert get_file._data_by_sections == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
            "<section=third>": "test",
        }
        get_file.reload()
        assert get_file._data_by_sections == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }

    def test_get_raw_data_content(self, get_file):
        raw_data = get_file.get_raw_data_content()
        assert (
            raw_data
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test_default_section_identifier(self, get_file):
        assert isinstance(get_file.default_section_separator, str)

    def test_section_separators_sorted(self, get_file):
        assert all([isinstance(x, str) for x in get_file.section_separators_sorted])

        assert [x for x in get_file.section_separators_sorted] == [
            "<section=first> ",
            "<section=second> ",
        ]

    def test_set_get_section_content(self, get_file):
        assert (
            get_file.set_section_content(
                section_separator="<section=a> ", section_content="some content"
            )
            is None
        )
        assert (
            get_file.get_section_content(section_separator="<section=a> ")
            == "some content"
        )

    def test_delete_all_sections_content(self, get_file):
        assert get_file.delete_all_sections_content() is None
        assert get_file._data_by_sections == {}

    def test_delete_section_content(self, get_file):
        get_file.set_section_content(
            section_separator="<section=a> ", section_content="some content"
        )
        assert get_file.delete_section_content(section_separator="<section=a> ") is None
        with pytest.raises(KeyError):
            get_file.get_section_content(section_separator="<section=a> ")

    def test_rename_section(self, get_file):
        get_file.set_section_content(
            section_separator="<section=a> ", section_content="some content"
        )

        assert (
            get_file.rename_section(
                old_section_separator="<section=a> ",
                new_section_separator="<section=b> ",
            )
            is None
        )

        assert (
            get_file.get_section_content(section_separator="<section=b> ")
            == "some content"
        )

        assert [
            section_separator
            for section_separator in get_file.section_separators_sorted
        ] == ["<section=b> ", "<section=first> ", "<section=second> ",]

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
