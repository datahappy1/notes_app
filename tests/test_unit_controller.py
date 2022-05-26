from notes_app.model.notes_model import NotesModel
from notes_app.view.notes_view import NotesView
from tests.conftest import DEFAULT_NOTES_FILE_PATH


class TestController:
    def test_controller(self, get_app):
        controller = get_app.controller
        assert controller
        assert isinstance(controller.model, NotesModel)
        assert isinstance(controller.view, NotesView)

    def test_set_file_path(self, get_app):
        controller = get_app.controller
        assert controller.set_file_path(file_path=DEFAULT_NOTES_FILE_PATH) is None

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
