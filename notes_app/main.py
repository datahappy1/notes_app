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


from notes_app.defaults import Defaults
from notes_app.settings import Settings
from notes_app.controller.notes_controller import NotesController
from notes_app.model.notes_model import NotesModel


class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        defaults = Defaults()
        settings = Settings(store=JsonStore, defaults=defaults)

        self.model = NotesModel(store=JsonStore, defaults=defaults)

        self.controller = NotesController(
            settings=settings, model=self.model, defaults=defaults
        )

    def _on_request_close(self, *source, **args):
        if self.controller.view.is_unsaved_change:
            self.controller.view.save_current_section_to_file()

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"

        self.icon = "assets/notes_app_logo.png"

        Window.bind(on_request_close=self._on_request_close)

        return self.controller.get_screen()


if __name__ == "__main__":
    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))
    NotesApp().run()
