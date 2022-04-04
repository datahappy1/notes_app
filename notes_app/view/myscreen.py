import os
from enum import Enum
from re import finditer

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from notes_app.utils.observer import Observer


SEARCH_LIST_ITEM_POSITION_STR = "Position "
SEARCH_LIST_ITEM_MATCHED_STR_ADDED_SURROUNDING_CHAR_COUNT = 30
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR = "ff0000"
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE = "b"


class OpenFilePopup(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowFileMetadataPopup(FloatLayout):
    show_file_metadata_label = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SearchPopup(FloatLayout):
    search_results_count = StringProperty(None)
    execute_search = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ScrollableLabel(ScrollView):
    pass


class CustomListItem(TwoLineListItem):
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
        self.menu = self.get_menu()
        self.popup = None
        self.last_searched_string = str()
        self.load_initial_data()

    def load_initial_data(self):
        self.text_view.text = self.controller.read_file_data()

        self.text_view.cursor = (2, 4)

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

    def execute_goto_search_result(self, custom_list_item):
        position = int(custom_list_item.secondary_text.replace(SEARCH_LIST_ITEM_POSITION_STR, ""))
        self.text_view.select_text(position, position + len(self.last_searched_string))

        cursor_position = self.text_view.get_cursor_from_index(position)
        self.text_view.cursor = cursor_position

        self.cancel_popup()

    def execute_search(self, *args):
        self.last_searched_string = args[0]
        self.popup.content.results_list.clear_widgets()

        text_data = self.text_view.text
        found_occurrences = [m.start() for m in finditer(self.last_searched_string, text_data)]

        if not found_occurrences:
            self.popup.content.search_results_count = "No match found"

        found_occurrences_count = len(found_occurrences)
        self.popup.content.search_results_count = f"Matches on {found_occurrences_count} positions found" \
            if found_occurrences_count > 1 else f"Match on {found_occurrences_count} position found"

        for position in found_occurrences:
            raw_sample = text_data[position:position+SEARCH_LIST_ITEM_MATCHED_STR_ADDED_SURROUNDING_CHAR_COUNT]

            sample = raw_sample.replace(
                self.last_searched_string,
                f"[{SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE}]"
                f"[color={SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR}]"
                f"{self.last_searched_string}"
                f"[/color]"
                f"[/{SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE}]"
            )

            sample += "..."

            self.popup.content.results_list.add_widget(
                CustomListItem(
                    text=sample,
                    secondary_text=f"{SEARCH_LIST_ITEM_POSITION_STR}{position}",
                    on_release=self.execute_goto_search_result,
                )
            )

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
            show_file_metadata_label=self.model.formatted,
            cancel=self.cancel_popup
        )
        self.popup = Popup(title="Show File metadata", content=content,
                           size_hint=(0.9, 0.9))
        self.popup.open()

    def press_icon_search(self, *args):
        content = SearchPopup(
            search_results_count="",
            execute_search=self.execute_search,
            cancel=self.cancel_popup
        )
        self.popup = Popup(title="Search", content=content,
                           size_hint=(0.9, 0.9))
        self.popup.open()


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
