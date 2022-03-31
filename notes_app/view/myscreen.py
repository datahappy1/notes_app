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
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from notes_app.utils.observer import Observer


class OpenFilePopup(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowFileMetadataPopup(FloatLayout):
    show_file_label = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SearchPopup(FloatLayout):
    search_results_count = StringProperty(None)
    search_results_markup = ObjectProperty(None)
    execute_search = ObjectProperty(None)
    cancel = ObjectProperty(None)


class CustomSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")


class MenuItems(Enum):
    ChooseFile = "Choose File"
    ShowFileInfo = "Show File info"
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
        self.menu = self.get_menu()
        self.popup = None
        self.load_initial_data()

    def load_initial_data(self):
        self.text_view.text = self.controller.read_file_data()

    def get_menu(self):
        menu_items = [
            {
                "text": f"{i.value}",
                "viewclass": "OneLineListItem",
                "height": dp(40),
                "on_release": lambda x=f"{i.value}": self.press_menu_item_callback(x),
            } for i in MenuItems
        ]
        return MDDropdownMenu(
            caller=self.ids.toolbar,
            items=menu_items,
            width_mult=5,
        )

    def press_menu_item_callback(self, text_item):
        if text_item == MenuItems.ChooseFile.value:
            self.press_menu_item_open_file()
        elif text_item == MenuItems.ShowFileInfo.value:
            self.press_menu_item_show_file_metadata()
        elif text_item == MenuItems.Save.value:
            self.press_menu_item_save_file()

        self.menu.dismiss()

    def notify_model_is_changed(self):
        """
        The method is called when the model changes.
        Requests and displays the value of the sum.
        """
        snackbar = CustomSnackbar(
            text="success!",
            icon="information",
            snackbar_x="10dp",
            snackbar_y="10dp"
        )
        snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
        snackbar.open()

    def execute_open_file(self, path, filename):
        file_path = filename[0]
        self.controller.set_file_path(file_path)

        self.text_view.text = self.controller.read_file_data(file_path=file_path)
        self.cancel_popup()

    def execute_search(self, *args):
        search_string = args[0]

        if search_string and search_string in self.text_view.text:
            file_data = self.controller.read_file_data()
            positions = []
            for item in file_data.split(" "):
                if search_string in item:
                    position = file_data.find(item)
                    positions.append(position)

            marked_file_data = file_data.replace(search_string, f"[b]{search_string}[/b]")
            self.popup.content.search_results_markup = marked_file_data

            item_count = len(positions)
            self.popup.content.search_results_count = \
                f"{str(item_count)} matches found" if item_count > 1 else f"{str(item_count)} match found"

        else:
            self.popup.content.search_results_markup = ""
            self.popup.content.search_results_count = "0 matches found"

    def cancel_popup(self):
        self.popup.dismiss()

    def press_menu_item_open_file(self, *args):
        content = OpenFilePopup(open_file=self.execute_open_file,
                                cancel=self.cancel_popup)
        self.popup = Popup(title="Open File", content=content,
                           size_hint=(0.9, 0.9))
        self.popup.open()

    def press_menu_item_save_file(self, *args):
        self.controller.save_file_data(data=self.text_view.text)

    def press_menu_item_show_file_metadata(self, *args):
        content = ShowFileMetadataPopup(
            show_file_label=f"{self.model.formatted}",
            cancel=self.cancel_popup
        )
        self.popup = Popup(title="Show File metadata", content=content,
                           size_hint=(0.9, 0.9))
        self.popup.open()

    def press_icon_search(self, *args):
        content = SearchPopup(
            search_results_count="",
            search_results_markup="",
            execute_search=self.execute_search,
            cancel=self.cancel_popup
        )
        self.popup = Popup(title="Search", content=content,
                           size_hint=(0.9, 0.9))
        self.popup.open()


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
