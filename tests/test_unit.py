import pytest
from kivymd.app import MDApp

from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel
from notes_app.settings import Settings

settings = Settings()


@pytest.fixture
def get_app():
    class NotesApp(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = MyScreenModel()
            self.controller = MyScreenController(settings=settings, model=self.model)

    return NotesApp()


def test1(get_app):
    assert get_app.model
    assert get_app.controller

    raw_file_data = get_app.controller.read_file_data()
    # print(raw_file_data)

    screen = get_app.controller.get_screen()
    print(screen.search.search_case_sensitive)
