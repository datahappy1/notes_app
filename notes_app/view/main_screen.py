import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.floatlayout import FloatLayout

KIVY_FILE_NAME = "main_screen.kv"


class OpenDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MainScreenView(BoxLayout):
    """"
    A class that implements the visual presentation `MyScreenModel`.
    """
    controller = ObjectProperty()
    model = ObjectProperty()

    open_button = ObjectProperty()
    save_button = ObjectProperty()
    search_button = ObjectProperty()
    text_view = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)  # register the view as an observer

    def set_c(self, focus, value):
        if not focus:
            self.controller.set_c(value)

    def set_d(self, focus, value):
        if not focus:
            self.controller.set_d(value)

    def model_is_changed(self):
        self.ids.result.text = str(self.model.sum)


Builder.load_file(os.path.join(os.path.dirname(__file__), KIVY_FILE_NAME))
