import os
from enum import Enum

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from notes_app.utils.observer import Observer


class OpenFileDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SearchContent(BoxLayout):
    pass


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
        self.open_file_dialog = OpenFileDialog()
        self.menu = self.get_menu()
        self.file_info_dialog = None
        self.search_dialog = None
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
            self.press_menu_item_show_metadata()
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
        self.cancel_open_file_popup()

    def execute_search(self, *args):
        search_string = self.search_dialog.content_cls.ids.search_string_text_field.text

        if search_string != "" and search_string in self.text_view.text:
            file_data = self.controller.read_file_data()

            for item in file_data.split(" "):
                if search_string in item:
                    position = (item, file_data.find(item))
                    self.search_dialog.content_cls.add_widget(OneLineListItem(text=f"{position}"))

        else:
            self.search_dialog.content_cls.ids.search_string_results_label.text = "no results"

    def cancel_open_file_popup(self):
        self.popup.dismiss()

    def cancel_file_info_dialog(self, *args):
        self.file_info_dialog.dismiss(force=True)
        self.file_info_dialog = None

    def cancel_search_dialog(self, *args):
        self.search_dialog.dismiss(force=True)
        self.search_dialog = None

    def press_menu_item_open_file(self, *args):
        content = OpenFileDialog(open_file=self.execute_open_file,
                                 cancel=self.cancel_open_file_popup)
        self.popup = Popup(title="Open File", content=content,
                           size_hint=(0.9, 0.9))
        self.popup.open()

    def press_menu_item_save_file(self, *args):
        self.controller.save_file_data(data=self.text_view.text)

    def press_menu_item_show_metadata(self, *args):
        if not self.file_info_dialog:
            self.file_info_dialog = MDDialog(
                title="File info",
                text=f"{self.model.formatted}",
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        theme_text_color="Custom",
                        on_release=self.cancel_file_info_dialog
                    )
                ],
            )
        self.file_info_dialog.open()

    def press_icon_search(self, *args):
        if not self.search_dialog:
            self.search_dialog = MDDialog(
                title="Search",
                text="What to search for?",
                type="custom",
                content_cls=SearchContent(),
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        on_release=self.execute_search
                    ),
                    MDFlatButton(
                        text="CLOSE",
                        theme_text_color="Custom",
                        on_release=self.cancel_search_dialog
                    )
                ],
            )
        self.search_dialog.open()


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
