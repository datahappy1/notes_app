from os import path, remove
from os.path import exists
from time import sleep

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

    def test_get_screen(self, get_app):
        controller = get_app.controller
        assert isinstance(controller.get_screen(), NotesView)
