import os
import sys

from kivy import Config
from kivy.resources import resource_add_path
from kivy.storage.jsonstore import JsonStore

Config.set("graphics", "window_state", "maximized")
Config.set("graphics", "multisamples", "0")
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.core.window import Window
from kivymd.app import MDApp

from notes_app.utils.settings import Settings
from notes_app.utils.default_notes_file import DefaultNotesFile
from notes_app.controller.notes_controller import NotesController
from notes_app.model.notes_model import NotesModel


class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.model = NotesModel(store=JsonStore, default_file=DefaultNotesFile())
        self.controller = NotesController(settings=Settings(store=JsonStore), model=self.model)

    def _on_request_close(self, *source, **args):
        if self.controller.view.is_unsaved_change:
            self.controller.view.save_current_section_to_file()

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"

        Window.bind(on_request_close=self._on_request_close)

        return self.controller.get_screen()


if __name__ == "__main__":
    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))
    NotesApp().run()
