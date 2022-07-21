import uuid

import pytest

from notes_app.file import get_validated_file_path

from notes_app.defaults import Defaults

defaults = Defaults()


def test_get_validated_file_path():
    file_path = defaults.DEFAULT_NOTES_FILE_NAME
    assert get_validated_file_path(file_path=file_path) == file_path

    file_path = f"sample_not_existing_{uuid.uuid4().hex}.txt"
    assert get_validated_file_path(file_path=file_path) is None


class TestSectionIdentifier:
    def test_section_identifier(self):
        with pytest.raises(ValueError):
            SectionIdentifier(defaults=defaults)

        with pytest.raises(ValueError):
            SectionIdentifier(
                defaults=defaults, section_file_separator="", section_name=""
            )

        assert (
            SectionIdentifier(
                defaults=defaults, section_file_separator="<section=a> "
            ).section_name
            == "a"
        )
        assert (
            SectionIdentifier(
                defaults=defaults, section_name="a"
            ).section_file_separator
            == "<section=a> "
        )


class TestFile:
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

    def test_reload(self, get_file):
        get_file.set_section_content(
            section_file_separator="<section=third>", section_content="test"
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

    def test__get_section_identifiers_from_raw_data_content(self, get_file):
        assert all(
            [
                isinstance(x, SectionIdentifier)
                for x in get_file._get_section_identifiers_from_raw_data_content()
            ]
        )

    def test_default_section_identifier(self, get_file):
        assert isinstance(get_file.default_section_separator, SectionIdentifier)

    def test_section_identifiers_sorted_by_name(self, get_file):
        assert all(
            [
                isinstance(x, SectionIdentifier)
                for x in get_file.section_separators_sorted
            ]
        )

        assert [
            x.section_name for x in get_file.section_separators_sorted
        ] == ["first", "second"]

    def test_add_section_identifier(self, get_file):
        assert (
            get_file.add_section_identifier(section_file_separator="<section=a> ")
            is None
        )
        assert len(get_file.section_separators_sorted) == 3
        assert all(
            [
                isinstance(x, SectionIdentifier)
                for x in get_file.section_separators_sorted
            ]
        )

    def test_delete_section_identifier(self, get_file):
        assert (
            get_file.delete_section_identifier(section_file_separator="<section=a> ")
            is None
        )
        assert len(get_file.section_separators_sorted) == 2
        assert all(
            [
                isinstance(x, SectionIdentifier)
                for x in get_file.section_separators_sorted
            ]
        )

    def test_delete_all_section_identifiers(self, get_file):
        assert get_file.delete_all_section_identifiers() is None
        assert get_file.section_separators_sorted == []

    def test_set_get_section_content(self, get_file):
        assert get_file.set_section_content(
            section_file_separator="<section=a> ", section_content="some content"
        ) is None
        assert (
            get_file.get_section_content(section_file_separator="<section=a> ")
            == "some content"
        )

    def test_delete_section_content(self, get_file):
        get_file.set_section_content(
            section_file_separator="<section=a> ", section_content="some content"
        )
        assert get_file.delete_section_content(
            section_file_separator="<section=a> "
        ) is None
        with pytest.raises(KeyError):
            get_file.get_section_content(section_file_separator="<section=a> ")

    def test_delete_all_sections_content(self, get_file):
        assert get_file.delete_all_sections_content() is None
        assert get_file.transform_data_by_sections_to_raw_data_content() == ""

    def test_rename_section(self, get_file):
        assert (
            get_file.add_section_identifier(section_file_separator="<section=a> ")
            is None
        )

        assert get_file.set_section_content(
            section_file_separator="<section=a> ", section_content="some content"
        ) is None

        assert [si.section_name for si in get_file._section_identifiers] == [
            "first",
            "second",
            "a",
        ]

        assert get_file.rename_section(
            old_section_separator="<section=a> ",
            new_section_separator="<section=b> ",
        ) is None

        assert (
            get_file.get_section_content(section_file_separator="<section=b> ")
            == "some content"
        )

        assert [si.section_name for si in get_file._section_identifiers] == [
            "first",
            "second",
            "b",
        ]

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
