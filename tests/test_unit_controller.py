from os import getcwd

import pytest
from kivymd.app import MDApp

from notes_app.controller.notes_controller import NotesController
from notes_app.model.notes_model import NotesModel, FALLBACK_NOTES_FILE_PATH
from notes_app.settings import Settings
from notes_app.view.notes_view import NotesView

settings = Settings()


@pytest.fixture
def get_app():
    class NotesApp(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = NotesModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
            self.controller = NotesController(settings=settings, model=self.model)

    return NotesApp()


class TestController:
    def test_controller(self, get_app):
        controller = get_app.controller
        assert controller
        assert isinstance(controller.model, NotesModel)
        assert isinstance(controller.view, NotesView)

    def test_set_file_path(self, get_app):
        controller = get_app.controller
        assert (
            controller.set_file_path(file_path=f"{getcwd()}/assets/sample.txt") is None
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
        assert (
            controller.save_file_data(
                data="""<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""
            )
            is None
        )

    def test_get_screen(self, get_app):
        controller = get_app.controller
        assert isinstance(controller.get_screen(), NotesView)
