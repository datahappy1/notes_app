import pytest

from time import sleep
from datetime import datetime
from os import path, remove, listdir, getcwd
from os.path import exists

from notes_app.defaults import Defaults
from notes_app.model.notes_model import NotesModel
from notes_app.view.notes_view import NotesView


class TestController:
    def test_controller(self, get_app):
        controller = get_app.controller
        assert controller
        assert isinstance(controller.model, NotesModel)
        assert isinstance(controller.view, NotesView)
        assert isinstance(controller.defaults, Defaults)

    def test__generate_default_file_if_not_exists(self, get_app):
        assert exists(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME)
        ts_before = path.getmtime(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME)

        remove(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME)
        assert not exists(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME)

        sleep(0.1)

        get_app.controller._generate_default_file_if_not_exists()

        assert exists(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME)

        ts_after = path.getmtime(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME)

        assert ts_after > ts_before

    def test_set_file_path(self, get_app):
        controller = get_app.controller
        assert (
            controller.set_file_path(
                file_path=get_app.model.defaults.DEFAULT_NOTES_FILE_NAME
            )
            is None
        )

    def test_read_file_data(self, get_app):
        controller = get_app.controller
        assert (
            controller.read_file_data()
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test_save_file_data(self, get_app):
        controller = get_app.controller

        assert controller.model.file_size == 0
        _epoch_before = datetime.fromtimestamp(controller.model.last_updated_on)
        assert _epoch_before

        assert (
            controller.save_file_data(
                data="""<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""
            )
            is None
        )

        assert isinstance(controller.model.file_size, int)
        assert controller.model.file_size > 0
        assert datetime.fromtimestamp(controller.model.last_updated_on) >= _epoch_before

    def test_save_file_data_handle_error(self, get_app):
        # test case to cover scenario when data write fails no data is lost
        controller = get_app.controller

        assert controller.model.file_size == 0
        _epoch_before = datetime.fromtimestamp(controller.model.last_updated_on)
        assert _epoch_before

        # asserting the default notes file contains data
        with open(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME, mode="r", encoding="utf8") as f:
            assert f.readlines() == ['<section=first> Quod equidem non reprehendo\n',
                                     '<section=second> Quis istum dolorem timet']

        controller.save_file_data(
                data="""<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""
        )

        assert isinstance(controller.model.file_size, int)
        # assert the model file_size is still > 0
        assert controller.model.file_size > 0  # exact file size differs between OS types

        # setting model file path as empty string is invalid enough to raise file write error exc
        controller.model.file_path = ""

        # writing to file through save_file_data raises Exception
        with pytest.raises(Exception):
            controller.save_file_data(
                data="""<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet <section=third> !
"""
            )

        # assert the file still contains the data
        with open(get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME, mode="r", encoding="utf8") as f:
            assert f.readlines() == ['<section=first> Quod equidem non reprehendo\n',
                                     '<section=second> Quis istum dolorem timet\n']

        assert isinstance(controller.model.file_size, int)
        # assert the model file_size is still > 0
        assert controller.model.file_size > 0  # exact file size differs between OS types
        assert datetime.fromtimestamp(controller.model.last_updated_on) >= _epoch_before

        # assert the file gets correctly dumped to disk
        dump_files_to_evaluate = []
        for file in listdir(getcwd()):
            if file.startswith("__dump__"):
                dump_files_to_evaluate.append(file)

        # assert only 1 dump file is written
        assert len(dump_files_to_evaluate) == 1
        with open(file=dump_files_to_evaluate[0], mode="r", encoding="utf8") as f:
            assert f.readlines() == ['<section=first> Quod equidem non reprehendo\n',
                                     '<section=second> Quis istum dolorem timet <section=third> !\n']

    def test_get_screen(self, get_app):
        controller = get_app.controller
        assert isinstance(controller.get_screen(), NotesView)
