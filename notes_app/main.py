from kivy.config import Config

Config.set("graphics", "window_state", "maximized")

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

    def build(self):
        # 'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue',
        # 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber',
        # 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray'
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"

        # '50', '100', '200', '300', '400', '500', '600', '700', '800', '900',
        # 'A100', 'A200', 'A400', 'A700'
        self.theme_cls.primary_hue = "A700"

        # 'Light', 'Dark'
        self.theme_cls.theme_style = "Dark"

        return self.controller.get_screen()


NotesApp().run()
