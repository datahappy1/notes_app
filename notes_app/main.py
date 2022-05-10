from kivy.config import Config

Config.set("graphics", "window_state", "maximized")
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.core.window import Window
from kivymd.app import MDApp

from notes_app.settings import Settings
from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel

settings = Settings()


class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = MyScreenModel()
        self.controller = MyScreenController(settings=settings, model=self.model)

    def _on_request_close(self, *source, **args):
        if self.controller.view.is_unsaved_change:
            self.controller.view.save_current_section_to_file()

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"

        Window.bind(on_request_close=self._on_request_close)

        return self.controller.get_screen()


NotesApp().run()
