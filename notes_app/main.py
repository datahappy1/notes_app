from kivy.app import App

from notes_app.controller.main_screen import MainScreenController
from notes_app.model.main_screen import MainScreenModel


class NotesApp(App):
    def __init__(self):
        App.__init__(self)
        self._model = MainScreenModel()
        self._controller = MainScreenController()

    def build(self):
        return self._controller.MainScreenController()


if __name__ == '__main__':
    NotesApp().run()
