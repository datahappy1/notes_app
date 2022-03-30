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
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from notes_app.utils.observer import Observer


class OpenFileDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class FileInfoDialog(FloatLayout):
    file_info_dialog_text = StringProperty(None)
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
        self._menu = self._setup_menu()
        self._search_dialog = None
        self._search_content = SearchContent()
        self._popup_choose_file = None
        self._popup_show_file_info = None
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
            width_mult=5,
        )

    def menu_callback(self, text_item):
        if text_item == MenuItems.ChooseFile.value:
            self.on_open()
        elif text_item == MenuItems.ShowFileInfo.value:
            self.on_show_metadata()
        elif text_item == MenuItems.Save.value:
            self.on_save()

        self._menu.dismiss()

    def model_is_changed(self):
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

    def cancel_choose_file_dialog(self):
        self._popup_choose_file.dismiss()

    def _open_file(self, path, filename):
        file_path = filename[0]
        self.controller.set_file_path(file_path)

        self.text_view.text = self.controller.read_file_data(file_path=file_path)
        self.cancel_choose_file_dialog()

    def on_open(self, *args):
        content = OpenFileDialog(open_file=self._open_file,
                                 cancel=self.cancel_choose_file_dialog)
        self._popup_choose_file = Popup(title="Open File", content=content,
                                        size_hint=(0.9, 0.9))
        self._popup_choose_file.open()

    def on_save(self, *args):
        self.controller.save_file_data(data=self.text_view.text)

    def close_file_info_dialog(self, *args):
        self._file_info_dialog.dismiss(force=True)
        self._file_info_dialog = None

    def cancel_show_file_dialog(self):
        self._popup_show_file_info.dismiss()

    def on_show_metadata(self, *args):
        content = FileInfoDialog(
            file_info_dialog_text=self.model.get_formatted(),#MDLabel(text=self.model.get_formatted()),
            cancel=self.cancel_show_file_dialog)
        # content = MDLabel(text=self.model.get_formatted())
        self._popup_show_file_info = Popup(title="File information",
                                           content=content,
                                           size_hint=(0.9, 0.9))
        self._popup_show_file_info.open()

    def close_search_dialog(self, *args):
        self._search_dialog.dismiss(force=True)
        self._search_dialog = None

    def execute_search(self, *args):
        search_string = self._search_dialog.content_cls.ids.search_string_text_field.text

        if search_string != "" and search_string in self.text_view.text:
            # self._search_dialog.dismiss()
            _mod_file_data = self.controller.read_file_data().replace(search_string, f"[b]{search_string}[/b]")

            self._search_dialog.content_cls.ids.search_string_results_label.text = _mod_file_data
        else:
            self._search_dialog.content_cls.ids.search_string_results_label.text = "no results"

    def on_search(self, *args):
        if not self._search_dialog:
            self._search_dialog = MDDialog(
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
                        on_release=self.close_search_dialog
                    )
                ],
            )
        self._search_dialog.open()


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
