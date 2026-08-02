import uuid
from os import listdir, getcwd

import pytest

from notes_app.defaults import Defaults
from notes_app.domain.notes_file import (
    get_validated_file_path,
)

defaults = Defaults()


def test_get_validated_file_path():
    file_path = defaults.DEFAULT_NOTES_FILE_NAME
    assert get_validated_file_path(file_path=file_path) == file_path

    file_path = f"sample_not_existing_{uuid.uuid4().hex}.txt"
    assert get_validated_file_path(file_path=file_path) is None


class TestNotesFile:
    def test__get_validated_raw_data(self, get_notes_file):
        raw_data = get_notes_file.get_raw_data_content()
        assert (
                get_notes_file._get_validated_raw_data(raw_data=raw_data)
                == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test_reload(self, get_notes_file):
        get_notes_file.set_section_content(
            section_separator="<section=third>", section_content="test"
        )
        assert get_notes_file._data_by_sections == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
            "<section=third>": "test",
        }
        get_notes_file.reload()
        assert get_notes_file._data_by_sections == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }

    def test_get_raw_data_content(self, get_notes_file):
        raw_data = get_notes_file.get_raw_data_content()
        assert (
            raw_data
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test_default_section_identifier(self, get_notes_file):
        assert isinstance(get_notes_file.default_section_separator, str)

    def test_section_separators_sorted(self, get_notes_file):
        assert all([isinstance(x, str) for x in get_notes_file.section_separators_sorted])

        assert [x for x in get_notes_file.section_separators_sorted] == [
            "<section=first> ",
            "<section=second> ",
        ]

    def test_set_get_section_content(self, get_notes_file):
        assert (
                get_notes_file.set_section_content(
                section_separator="<section=a> ", section_content="some content"
            )
                is None
        )
        assert (
                get_notes_file.get_section_content(section_separator="<section=a> ")
                == "some content"
        )

    def test_delete_all_sections_content(self, get_notes_file):
        assert get_notes_file.delete_all_sections_content() is None
        assert get_notes_file._data_by_sections == {}

    def test_delete_section_content(self, get_notes_file):
        get_notes_file.set_section_content(
            section_separator="<section=a> ", section_content="some content"
        )
        assert get_notes_file.delete_section_content(section_separator="<section=a> ") is None
        with pytest.raises(KeyError):
            get_notes_file.get_section_content(section_separator="<section=a> ")

    def test_rename_section(self, get_notes_file):
        get_notes_file.set_section_content(
            section_separator="<section=a> ", section_content="some content"
        )

        assert (
                get_notes_file.rename_section(
                old_section_separator="<section=a> ",
                new_section_separator="<section=b> ",
            )
                is None
        )

        assert (
                get_notes_file.get_section_content(section_separator="<section=b> ")
                == "some content"
        )

        assert [
            section_separator
            for section_separator in get_notes_file.section_separators_sorted
        ] == ["<section=b> ", "<section=first> ", "<section=second> ",]

    def test__transform_raw_data_content_to_data_by_sections(self, get_notes_file):
        assert get_notes_file._transform_raw_data_content_to_data_by_sections() == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }

    def test_transform_data_by_sections_to_raw_data_content(self, get_notes_file):
        assert (
                get_notes_file.transform_data_by_sections_to_raw_data_content()
                == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test_save_file_data(self, get_notes_file):
        get_notes_file._raw_data_content = """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        assert (
                get_notes_file.save_file_data() is None
        )

    def test_save_file_data_handle_error(self, get_app, get_notes_file):
        # test case to cover scenario when data write fails no data is lost
        get_notes_file._raw_data_content = """<section=first> Quod equidem non reprehendo
        <section=second> Quis istum dolorem timet <section=third> !"""
        get_notes_file._data_by_sections = get_notes_file._transform_raw_data_content_to_data_by_sections()

        get_notes_file._file_path = None
        # writing to file through save_file_data raises Exception
        with pytest.raises(Exception):
            get_notes_file.save_file_data()

        # assert the file still contains the data
        with open(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME, mode="r", encoding="utf8") as f:
            assert [l.strip() for l in f.readlines()] == [
                '<section=first> Quod equidem non reprehendo',
                '<section=second> Quis istum dolorem timet'
            ]

        # assert the file gets correctly dumped to disk
        dump_files_to_evaluate = []
        for file in listdir(getcwd()):
            if file.startswith("__dump__"):
                dump_files_to_evaluate.append(file)

        # assert only 1 dump file is written
        assert len(dump_files_to_evaluate) == 1
        with open(file=dump_files_to_evaluate[0], mode="r", encoding="utf8") as f:
            assert [l.strip() for l in f.readlines()] == [
                '<section=first> Quod equidem non reprehendo',
                '<section=second> Quis istum dolorem timet <section=third> !'
            ]
