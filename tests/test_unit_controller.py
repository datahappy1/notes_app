from time import sleep
from datetime import datetime
from os import path, remove
from os.path import exists

from notes_app.defaults import Defaults
from notes_app.model.notes_model import NotesModel
from notes_app.view.notes_view import NotesView


class TestController:
    def test_controller(self, get_app):
        controller = get_app.controller
        assert controller
        assert isinstance(controller._model, NotesModel)
        assert isinstance(controller._view, NotesView)
        assert isinstance(controller._defaults, Defaults)

    def test__generate_default_file_if_not_exists(self, get_app):
        assert exists(get_app.controller._defaults.DEFAULT_NOTES_FILE_NAME)
        ts_before = path.getmtime(get_app.controller._defaults.DEFAULT_NOTES_FILE_NAME)

        remove(get_app.controller._defaults.DEFAULT_NOTES_FILE_NAME)
        assert not exists(get_app.controller._defaults.DEFAULT_NOTES_FILE_NAME)

        sleep(0.1)

        get_app.controller._generate_default_file_if_not_exists()

        assert exists(get_app.controller._defaults.DEFAULT_NOTES_FILE_NAME)

        ts_after = path.getmtime(get_app.controller._defaults.DEFAULT_NOTES_FILE_NAME)

        assert ts_after > ts_before

    def test_set_file_path(self, get_app):
        controller = get_app.controller
        assert (
            controller.set_file_path(
                file_path=get_app.model._defaults.DEFAULT_NOTES_FILE_NAME
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

        assert controller._model.file_size == 0
        _epoch_before = datetime.fromtimestamp(controller._model.last_updated_on)
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

    def test_get_screen(self, get_app):
        controller = get_app.controller
        assert isinstance(controller.get_screen(), NotesView)
