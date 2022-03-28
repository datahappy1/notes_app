import os
from enum import Enum

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from notes_app.utils.observer import Observer


class OpenDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class CustomSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")


class MenuItems(Enum):
    ChooseFile = "Choose File"
    Search = "Search"
    Save = "Save"


class MyScreenView(BoxLayout, MDScreen, Observer):
    """"
    A class that implements the visual presentation `MyScreenModel`.

    """
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)  # register the view as an observer
        self.open_dialog = OpenDialog()
        self.save_dialog = SaveDialog()
        self.menu = self._setup_menu()
        #self.lbl = NoneCustomLabel()
        self._popup = None
        self._on_startup()

    def _on_startup(self):
        self.text_view.text = self.controller.read_file_data()

    def _setup_menu(self):
        menu_items = [
            {
                "text": f"{i.value}",
                "viewclass": "OneLineListItem",
                "height": dp(40),
                "on_release": lambda x=f"{i.value}": self.menu_callback(x),
            } for i in MenuItems
        ]
        return MDDropdownMenu(
            caller=self.ids.toolbar,
            items=menu_items,
            width_mult=2,
        )

    def menu_callback(self, text_item):
        if text_item == MenuItems.Save.value:
            self.on_save()
        elif text_item == MenuItems.ChooseFile.value:
            self.on_open()
        elif text_item == MenuItems.Search.value:
            pass

        self.menu.dismiss()

    def model_is_changed(self):
        """
        The method is called when the model changes.
        Requests and displays the value of the sum.
        """
        snackbar = CustomSnackbar(
            text="All is saved!",
            icon="information",
            snackbar_x="10dp",
            snackbar_y="10dp"
        )
        snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
        snackbar.open()

        self.lbl.text = f"{self.model.metadata}"

    def cancel_dialog(self):
        self._popup.dismiss()

    def _open_file(self, path, filename):
        file_path = filename[0]
        self.controller.set_file_path(file_path)

        self.text_view.text = self.controller.read_file_data(file_path=file_path)
        self.cancel_dialog()

    def on_open(self, *args):
        content = OpenDialog(open_file=self._open_file,
                             cancel=self.cancel_dialog)
        self._popup = Popup(title="Open File", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def on_save(self, *args):
        self.controller.save_file_data(data=self.text_view.text)

    def on_search(self, *args):
        pass


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
