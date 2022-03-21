from kivymd.app import MDApp

from notes_app.controller.main_screen import MainScreenController
from notes_app.model.main_screen import MainScreenModel


class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = MainScreenModel()
        self._controller = MainScreenController(self._model)

    def build(self):
        return self._controller.get_screen()


if __name__ == '__main__':
    NotesApp().run()
