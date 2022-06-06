import time

from notes_app.model.notes_model import NotesModel
from notes_app.view.notes_view import NotesView
from tests.conftest import TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH


class TestController:
    def test_controller(self, get_app):
        controller = get_app.controller
        assert controller
        assert isinstance(controller.model, NotesModel)
        assert isinstance(controller.view, NotesView)

    def test_set_file_path(self, get_app):
        controller = get_app.controller
        assert (
            controller.set_file_path(file_path=TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH)
            is None
        )

    def test_read_file_data(self, get_app):
        controller = get_app.controller
        assert (
            controller.read_file_data()
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

    def test__check_is_external_update(self, get_app):
        controller = get_app.controller
        assert controller._check_is_external_update() is True

        # now set controller.model.last_updated_on to current epoch time
        controller.model.last_updated_on = time.time()
        assert controller._check_is_external_update() is False

    def test_save_file_data(self, get_app):
        controller = get_app.controller
        # controller.model.last_updated_on check_is_external_update check return True
        assert (
            controller.save_file_data(
                data="""<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""
            )
            is True
        )

        # now set controller.model.last_updated_on to current epoch time
        # to have check_is_external_update check return False
        controller.model.last_updated_on = time.time()
        assert (
            controller.save_file_data(
                data="""<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""
            )
            is False
        )

    def test_get_screen(self, get_app):
        controller = get_app.controller
        assert isinstance(controller.get_screen(), NotesView)
