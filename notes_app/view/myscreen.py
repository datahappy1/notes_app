import webbrowser
from enum import Enum
from os import path, linesep

from kivy.core.text import Label
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import BubbleButton, Bubble
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, ThreeLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from notes_app.observer.observer import Observer
from notes_app.utils.color import get_color_by_name, get_next_color_by_rgba
from notes_app.utils.file import (
    File,
    SectionIdentifier,
    SECTION_FILE_NEW_SECTION_PLACEHOLDER,
    SECTION_FILE_NAME_MINIMAL_CHAR_COUNT,
)
from notes_app.utils.font import get_next_font
from notes_app.utils.search import Search

APP_TITLE = "Notes"

SEARCH_MINIMAL_CHAR_COUNT = 2
SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE = "section "
SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE = "position "
SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT = 30
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR = "ff0000"
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE = "b"

EXTERNAL_REPOSITORY_URL = "https://www.github.com/datahappy1/notes_app/"

APP_METADATA_ROWS = ["A simple notes application", "built with Python 3.7 & KivyMD"]

AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT = 5


class ItemDrawer(OneLineAvatarIconListItem):
    icon = StringProperty()
    id = StringProperty()
    text = StringProperty()
    delete = ObjectProperty()


class ContentNavigationDrawer(BoxLayout):
    pass


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        """
        Called when tap on a menu item
        Set the color of the icon and text for the menu item.
        """
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color


class OpenFilePopup(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowFileMetadataPopup(FloatLayout):
    show_file_metadata_label = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowAppMetadataPopup(FloatLayout):
    show_app_metadata_label = ObjectProperty(None)
    execute_goto_external_url = ObjectProperty(None)
    cancel = ObjectProperty(None)


class AddSectionPopup(FloatLayout):
    add_section_result_message = StringProperty(None)
    execute_add_section = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MyToggleButton(MDFlatButton, MDToggleButton):
    pass


class SearchPopup(FloatLayout):
    get_search_switch_state = ObjectProperty(None)
    switch_callback = ObjectProperty(None)
    search_string_placeholder = StringProperty(None)
    search_results_message = StringProperty(None)
    execute_search = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ScrollableLabel(ScrollView):
    pass


class CustomListItem(ThreeLineListItem):
    pass


class CustomSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    # font_size = NumericProperty("15sp")


class MenuStorageItems(Enum):
    ChooseFile = "Choose storage file"
    ShowFileInfo = "Show storage file info"
    Save = "Save storage file"


class MenuSettingsItems(Enum):
    SetNextFont = "Set next font"
    IncreaseFontSize = "Increase font size"
    DecreaseFontSize = "Decrease font size"
    SetNextBackgroundColor = "Set next background color"
    SetNextForegroundColor = "Set next foreground color"
    SaveSettings = "Save settings"
    ShowAppInfo = "Show application info"


# ###
class CustomBubbleButton(BubbleButton):
    pass


class NumericKeyboard(Bubble):
    layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NumericKeyboard, self).__init__(**kwargs)
        self.create_bubble_button()

    def create_bubble_button(self):
        numeric_keypad = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '', '0', '.']
        for x in numeric_keypad:
            if len(x) == 0:
                pass # self.layout.add_widget(Label(text=""))
            else:
                bubb_btn = CustomBubbleButton(text=str(x))
                self.layout.add_widget(bubb_btn)
# ###


class MyScreenView(BoxLayout, MDScreen, Observer, Bubble):
    """"
    A class that implements the visual presentation `MyScreenModel`.

    """

    settings = ObjectProperty()

    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)  # register the view as an observer

        self.menu_storage = self.get_menu_storage()
        self.menu_settings = self.get_menu_settings()
        self.popup = None
        self.snackbar = None

        self.last_searched_string = str()
        self.auto_save_text_input_change_counter = 0

        self.file = File(file_path=None, controller=self.controller)

        self.current_section_identifier = self.file.default_section_identifier
        self.search = Search()

        self.filter_data_split_by_section()
        self.set_drawer_items(section_identifiers=self.file.section_identifiers)

        self.set_properties_from_settings()

    @property
    def is_unsaved_change(self):
        return self.auto_save_text_input_change_counter > 0

    def set_properties_from_settings(self):
        self.text_section_view.font_name = self.settings.font_name
        self.text_section_view.font_size = self.settings.font_size
        self.text_section_view.background_color = get_color_by_name(
            self.settings.background_color
        ).rgba_value
        self.text_section_view.foreground_color = get_color_by_name(
            self.settings.foreground_color
        ).rgba_value

    def filter_data_split_by_section(self, section_identifier=None):
        section_identifier = section_identifier or self.current_section_identifier

        self.text_section_view.section_file_separator = (
            section_identifier.section_file_separator
        )

        self.text_section_view.text = self.file.get_section_content(
            section_file_separator=section_identifier.section_file_separator
        )
        # setting self.text_section_view.text invokes the on_text event method
        # but changing the section without any actual typing is not an unsaved change
        self.auto_save_text_input_change_counter = 0

        self.ids.toolbar.title = (
            f"{APP_TITLE} section: {section_identifier.section_name}"
        )

    def set_drawer_items(self, section_identifiers):
        self.ids.md_list.clear_widgets()

        for section_identifier in section_identifiers:
            self.ids.md_list.add_widget(
                ItemDrawer(
                    icon="bookmark",
                    id=section_identifier.section_file_separator,
                    text=f"section: {section_identifier.section_name}",
                    on_release=lambda x=f"{section_identifier.section_file_separator}": self.press_drawer_item_callback(
                        x
                    ),
                    delete=self.press_delete_section,
                )
            )

    def press_drawer_item_callback(self, text_item):
        if self.is_unsaved_change:
            self.save_current_section_to_file()

        section_identifier = SectionIdentifier(section_file_separator=text_item.id)
        self.current_section_identifier = section_identifier
        self.filter_data_split_by_section()

    def get_menu_storage(self):
        menu_items = [
            {
                "text": f"{i.value}",
                "viewclass": "OneLineListItem",
                # "height": dp(40),
                "on_release": lambda x=f"{i.value}": self.press_menu_storage_item_callback(
                    x
                ),
            }
            for i in MenuStorageItems
        ]
        return MDDropdownMenu(caller=self.ids.toolbar, items=menu_items, width_mult=5,)

    def get_menu_settings(self):
        menu_items = [
            {
                "text": f"{i.value}",
                "viewclass": "OneLineListItem",
                # "height": dp(40),
                "on_release": lambda x=f"{i.value}": self.press_menu_settings_item_callback(
                    x
                ),
            }
            for i in MenuSettingsItems
        ]
        return MDDropdownMenu(caller=self.ids.toolbar, items=menu_items, width_mult=5,)

    def press_menu_storage_item_callback(self, text_item):
        if text_item == MenuStorageItems.ChooseFile.value:
            self.press_menu_item_open_file()
        elif text_item == MenuStorageItems.ShowFileInfo.value:
            self.press_menu_item_show_file_metadata()
        elif text_item == MenuStorageItems.Save.value:
            self.press_menu_item_save_file()

        self.menu_storage.dismiss()

    def press_menu_settings_item_callback(self, text_item):
        if text_item == MenuSettingsItems.SetNextFont.value:
            next_font = get_next_font(font_name=self.text_section_view.font_name)
            self.text_section_view.font_name = next_font
            self.settings.font_name = next_font
        elif text_item == MenuSettingsItems.IncreaseFontSize.value:
            self.text_section_view.font_size += 1
            self.settings.font_size = self.text_section_view.font_size
        elif text_item == MenuSettingsItems.DecreaseFontSize.value:
            self.text_section_view.font_size -= 1
            self.settings.font_size = self.text_section_view.font_size
        elif text_item == MenuSettingsItems.SetNextBackgroundColor.value:
            next_background_color = get_next_color_by_rgba(
                rgba_value=self.text_section_view.background_color,
                skip_rgba_value=self.text_section_view.foreground_color
            )
            self.text_section_view.background_color = next_background_color.rgba_value
            self.settings.background_color = next_background_color.name
        elif text_item == MenuSettingsItems.SetNextForegroundColor.value:
            next_foreground_color = get_next_color_by_rgba(
                rgba_value=self.text_section_view.foreground_color,
                skip_rgba_value=self.text_section_view.background_color
            )
            self.text_section_view.foreground_color = next_foreground_color.rgba_value
            self.settings.foreground_color = next_foreground_color.name
        elif text_item == MenuSettingsItems.SaveSettings.value:
            self.settings.dump()
            self.menu_settings.dismiss()
        elif text_item == MenuSettingsItems.ShowAppInfo.value:
            self.press_menu_item_show_app_metadata()
            self.menu_settings.dismiss()

    def notify_model_is_changed(self):
        """
        The method is called when the model changes.
        Requests and displays the value of the sum.
        """
        self.snackbar = CustomSnackbar(
            text="changes saved",
            icon="information",
            snackbar_x="10dp",
            snackbar_y="10dp"
        )
        self.snackbar.size_hint_x = (Window.width - (self.snackbar.snackbar_x * 2)) / Window.width
        self.snackbar.open()

    def show_error_bar(self, error_message):
        """
        The method is called when the model changes.
        Requests and displays the value of the sum.
        """
        self.snackbar = CustomSnackbar(
            text=error_message,
            icon="alert-circle",
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        self.snackbar.size_hint_x = (Window.width - (self.snackbar.snackbar_x * 2)) / Window.width
        self.snackbar.open()

    def execute_open_file(self, path, filename):
        if not filename:
            return

        file_path = filename[0]
        self.controller.set_file_path(file_path)

        try:
            self.file = File(file_path=file_path, controller=self.controller)
            self.set_drawer_items(section_identifiers=self.file.section_identifiers)
            self.filter_data_split_by_section(
                section_identifier=self.file.default_section_identifier
            )
            self.cancel_popup()

        except ValueError:
            self.file.delete_all_section_identifiers()
            self.file.delete_all_sections_content()
            self.cancel_popup()
            self.press_add_section()

    def execute_goto_search_result(self, custom_list_item):
        section_name = custom_list_item.secondary_text.replace(
            SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE, ""
        )

        self.current_section_identifier = SectionIdentifier(section_name=section_name)
        self.filter_data_split_by_section()

        position = int(
            custom_list_item.tertiary_text.replace(
                SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE, ""
            )
        )

        self.text_section_view.select_text(
            position, position + len(self.last_searched_string)
        )

        cursor_position = self.text_section_view.get_cursor_from_index(position)
        self.text_section_view.cursor = cursor_position

        self.cancel_popup()

    def get_search_switch_state(self, switch_id):
        if switch_id == "search_case_sensitive_switch":
            return self.search.search_case_sensitive
        elif switch_id == "search_all_sections_switch":
            return self.search.search_all_sections

    def switch_callback(self, switch_id, state, *args):
        if switch_id == "search_case_sensitive_switch":
            self.search.search_case_sensitive = state
        elif switch_id == "search_all_sections_switch":
            self.search.search_all_sections = state

    def execute_search(self, *args):
        if not args[0] or len(args[0]) < SEARCH_MINIMAL_CHAR_COUNT or args[0].isspace():
            self.popup.content.search_results_message = "Invalid search"
            return

        self.last_searched_string = args[0]

        self.popup.content.results_list.clear_widgets()

        found_occurrences = self.search.search_for_occurrences(
            pattern=self.last_searched_string,
            file=self.file,
            current_section_identifier=self.current_section_identifier,
        )

        if not found_occurrences:
            self.popup.content.search_results_message = "No match found"
            return

        found_occurrences_count = 0

        for (
            section_file_separator,
            section_found_occurrences,
        ) in found_occurrences.items():
            found_occurrences_count += len(section_found_occurrences)
            text_data = self.file.get_section_content(section_file_separator)

            for position_start in section_found_occurrences:
                position_end = position_start + len(self.last_searched_string)

                found_string = text_data[position_start:position_end]

                found_string_marked = (
                    f"[{SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE}]"
                    f"[color={SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR}]"
                    f"{found_string}"
                    f"[/color]"
                    f"[/{SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE}]"
                )

                found_string_extra_chars = text_data[
                    position_end: position_end
                    + SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT
                ]

                section_identifier = SectionIdentifier(
                    section_file_separator=section_file_separator
                )

                self.popup.content.results_list.add_widget(
                    CustomListItem(
                        text=f"{found_string_marked}{found_string_extra_chars}...",
                        secondary_text=f"{SEARCH_LIST_ITEM_SECTION_DISPLAY_VALUE}{section_identifier.section_name}",
                        tertiary_text=f"{SEARCH_LIST_ITEM_POSITION_DISPLAY_VALUE}{position_start}",
                        on_release=self.execute_goto_search_result,
                    )
                )

        self.popup.content.search_results_message = (
            f"Matches on {found_occurrences_count} positions found"
            if found_occurrences_count > 1
            else f"Match on {found_occurrences_count} position found"
        )

    def execute_add_section(self, *args):
        if (
            not args[0]
            or len(args[0]) < SECTION_FILE_NAME_MINIMAL_CHAR_COUNT
            or args[0].isspace()
        ):
            self.popup.content.add_section_result_message = "Invalid name"
            return

        section_name = args[0]
        section_identifier = SectionIdentifier(section_name=section_name)

        if section_identifier.section_file_separator in self.file.section_identifiers:
            self.popup.content.add_section_result_message = "Name already exists"
            return

        self.file.add_section_identifier(
            section_file_separator=section_identifier.section_file_separator
        )
        self.file.set_section_content(
            section_file_separator=section_identifier.section_file_separator,
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )

        self.filter_data_split_by_section(section_identifier=section_identifier)

        self.set_drawer_items(section_identifiers=self.file.section_identifiers)

        self.cancel_popup()

    def execute_goto_external_url(self):
        return webbrowser.open(EXTERNAL_REPOSITORY_URL)

    def cancel_popup(self):
        self.popup.dismiss()
        self.popup = Popup()  # TODO check

    def press_menu_item_open_file(self, *args):
        content = OpenFilePopup(
            open_file=self.execute_open_file, cancel=self.cancel_popup
        )
        self.popup = Popup(
            title="Open File",
            content=content,
            # size_hint=(0.9, 0.9)
        )
        self.popup.open()

    def save_current_section_to_file(self):
        self.file.set_section_content(
            section_file_separator=self.text_section_view.section_file_separator,
            section_content=self.text_section_view.text,
        )

        text_data = self.file.transform_data_by_sections_to_raw_data_content()

        self.controller.save_file_data(data=text_data)

    def press_menu_item_save_file(self, *args):
        self.save_current_section_to_file()

    def press_menu_item_show_file_metadata(self, *args):
        content = ShowFileMetadataPopup(
            show_file_metadata_label=self.model.formatted, cancel=self.cancel_popup
        )
        self.popup = Popup(
            title="Show File metadata",
            content=content,
            # size_hint=(0.9, 0.9)
        )
        self.popup.open()

    def press_menu_item_show_app_metadata(self, *args):
        app_info = linesep.join(APP_METADATA_ROWS)

        content = ShowAppMetadataPopup(
            show_app_metadata_label=app_info,
            execute_goto_external_url=self.execute_goto_external_url,
            cancel=self.cancel_popup,
        )
        self.popup = Popup(
            title="Show App metadata",
            content=content,
            # size_hint=(0.9, 0.9)
        )
        self.popup.open()

    def press_icon_search(self, *args):
        content = SearchPopup(
            get_search_switch_state=self.get_search_switch_state,
            switch_callback=self.switch_callback,
            search_string_placeholder=self.last_searched_string,
            search_results_message="",
            execute_search=self.execute_search,
            cancel=self.cancel_popup,
        )
        self.popup = Popup(
            title="Search",
            content=content,
            # size_hint=(0.9, 0.9)
        )
        self.popup.open()

    def press_add_section(self, *args):
        content = AddSectionPopup(
            add_section_result_message="",
            execute_add_section=self.execute_add_section,
            cancel=self.cancel_popup,
        )
        self.popup = Popup(
            title="Add section",
            content=content,
            # size_hint=(0.9, 0.9)
        )
        self.popup.open()

    def press_delete_section(self, section_item):
        if len(self.file.section_identifiers) == 1:
            self.show_error_bar(error_message="Cannot delete last section")
            return

        self.ids.md_list.remove_widget(section_item)

        self.file.delete_section_identifier(section_file_separator=section_item.id)
        self.file.delete_section_content(section_file_separator=section_item.id)

        self.filter_data_split_by_section(
            section_identifier=self.file.default_section_identifier
        )

    def text_input_changed_callback(self):
        self.auto_save_text_input_change_counter += 1

        if (
            self.auto_save_text_input_change_counter
            == AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT
        ):
            self.save_current_section_to_file()
            self.auto_save_text_input_change_counter = 0

    # ###
    # https://stackoverflow.com/questions/47552735/kivy-python-textinput-display-bubble
    text_input = ObjectProperty(None)
    def show_bubble(self, *l):
        if not hasattr(self, 'bubb'):
            self.bubb = bubb = NumericKeyboard()
            self.bubb.arrow_pos = "bottom_mid"
            self.add_widget(bubb)
    # ###


Builder.load_file(path.join(path.dirname(__file__), "myscreen.kv"))
