import os
import webbrowser
from enum import Enum
from os import path, linesep
from os.path import exists

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
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
from notes_app.utils.file_sync import SUPPORTED_SYNC_PROVIDERS
from notes_app.utils.font import get_next_font
from notes_app.utils.mark import get_marked_search_result
from notes_app.utils.search import (
    Search,
    validate_search_input,
    SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT,
    transform_section_text_placeholder_to_section_name,
    transform_section_name_to_section_text_placeholder,
    transform_position_text_placeholder_to_position,
    transform_position_to_position_text_placeholder,
)
from notes_app.utils.text_input import AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT

APP_TITLE = "Notes"
APP_METADATA_ROWS = ["A simple notes application", "built with Python 3.8 & KivyMD"]
EXTERNAL_REPOSITORY_URL = "https://www.github.com/datahappy1/notes_app/"


class ItemDrawer(OneLineAvatarIconListItem):
    icon = StringProperty()
    id = StringProperty()
    text = StringProperty()
    delete = ObjectProperty()


class ContentNavigationDrawer(MDBoxLayout):
    pass


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        """Called when tap on a menu item.
        Set the color of the icon and text for the menu item.
        """
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color


class OpenFileDialogContent(MDBoxLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowFileMetadataDialogContent(MDBoxLayout):
    show_file_metadata_label = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowAppMetadataDialogContent(MDBoxLayout):
    show_app_metadata_label = ObjectProperty(None)
    execute_goto_external_url = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ShowFileSyncOptionsDialogContent(MDBoxLayout):
    show_file_sync_options_label = ObjectProperty(None)
    cancel = ObjectProperty(None)


class AddSectionDialogContent(MDBoxLayout):
    add_section_result_message = StringProperty(None)
    execute_add_section = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SearchDialogContent(MDBoxLayout):
    get_search_switch_state = ObjectProperty(None)
    search_switch_callback = ObjectProperty(None)
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


class MenuStorageItems(Enum):
    ChooseFile = "Choose storage file"
    ShowFileInfo = "Show storage file info"
    Save = "Save storage file"
    SyncOptions = "Sync options"


class MenuSettingsItems(Enum):
    SetNextFont = "Set next font"
    IncreaseFontSize = "Increase font size"
    DecreaseFontSize = "Decrease font size"
    SetNextBackgroundColor = "Set next background color"
    SetNextForegroundColor = "Set next foreground color"
    SaveSettings = "Save settings"
    ShowAppInfo = "Show application info"


class MyScreenView(MDBoxLayout, MDScreen, Observer):
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
        self.snackbar = None
        self.dialog = None

        self.manager_open = False
        self.file_manager = None

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
                    icon="bookmark-outline",
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
                "height": dp(40),
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
                "height": dp(40),
                "on_release": lambda x=f"{i.value}": self.press_menu_settings_item_callback(
                    x
                ),
            }
            for i in MenuSettingsItems
        ]
        return MDDropdownMenu(caller=self.ids.toolbar, items=menu_items, width_mult=5,)

    def get_file_manager(self):
        return MDFileManager(
            exit_manager=self.cancel_file_manager,
            select_path=self.file_manager_select_path,
        )

    def press_menu_storage_item_callback(self, text_item):
        if text_item == MenuStorageItems.ChooseFile.value:
            self.press_menu_item_open_file()
        elif text_item == MenuStorageItems.ShowFileInfo.value:
            self.press_menu_item_show_file_metadata()
        elif text_item == MenuStorageItems.Save.value:
            self.press_menu_item_save_file()
        elif text_item == MenuStorageItems.SyncOptions.value:
            self.press_menu_item_open_sync_options()

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
                skip_rgba_value=self.text_section_view.foreground_color,
            )
            self.text_section_view.background_color = next_background_color.rgba_value
            self.settings.background_color = next_background_color.name
        elif text_item == MenuSettingsItems.SetNextForegroundColor.value:
            next_foreground_color = get_next_color_by_rgba(
                rgba_value=self.text_section_view.foreground_color,
                skip_rgba_value=self.text_section_view.background_color,
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
            snackbar_y="10dp",
        )
        self.snackbar.size_hint_x = (
            Window.width - (self.snackbar.snackbar_x * 2)
        ) / Window.width
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
        self.snackbar.size_hint_x = (
            Window.width - (self.snackbar.snackbar_x * 2)
        ) / Window.width
        self.snackbar.open()

    def execute_open_file(self, file_path):
        if not file_path or not exists(file_path):
            self.show_error_bar(error_message="Invalid file")
            return

        validated_file_path = File.get_validated_file_path(file_path)
        if not validated_file_path:
            self.show_error_bar(error_message=f"Cannot open the file {file_path}")
            return

        self.controller.set_file_path(validated_file_path)

        try:
            self.file = File(file_path=validated_file_path, controller=self.controller)
            self.set_drawer_items(section_identifiers=self.file.section_identifiers)
            self.filter_data_split_by_section(
                section_identifier=self.file.default_section_identifier
            )
        except ValueError:
            self.file.delete_all_section_identifiers()
            self.file.delete_all_sections_content()
            self.press_add_section()

    def execute_goto_search_result(self, custom_list_item):
        section_name = transform_section_text_placeholder_to_section_name(
            section_text_placeholder=custom_list_item.secondary_text
        )

        self.current_section_identifier = SectionIdentifier(section_name=section_name)
        self.filter_data_split_by_section()

        position = transform_position_text_placeholder_to_position(
            position_text_placeholder=custom_list_item.tertiary_text
        )

        self.text_section_view.select_text(
            position, position + len(self.last_searched_string)
        )

        cursor_position = self.text_section_view.get_cursor_from_index(position)
        self.text_section_view.cursor = cursor_position

        self.cancel_dialog()

    def get_search_switch_state(self, switch_id):
        if switch_id == "search_case_sensitive_switch":
            return self.search.search_case_sensitive
        elif switch_id == "search_all_sections_switch":
            return self.search.search_all_sections
        elif switch_id == "search_full_words_switch":
            return self.search.search_full_words

    def search_switch_callback(self, switch_id, state, *args):
        if switch_id == "search_case_sensitive_switch":
            self.search.search_case_sensitive = state
        elif switch_id == "search_all_sections_switch":
            self.search.search_all_sections = state
        elif switch_id == "search_full_words_switch":
            self.search.search_full_words = state

    def execute_search(self, *args):
        if not validate_search_input(input_string=args[0]):
            self.dialog.content_cls.search_results_message = "Invalid search"
            return

        self.last_searched_string = args[0]

        self.dialog.content_cls.results_list.clear_widgets()

        found_occurrences = self.search.search_for_occurrences(
            pattern=self.last_searched_string,
            file=self.file,
            current_section_identifier=self.current_section_identifier,
        )

        if not found_occurrences:
            self.dialog.content_cls.search_results_message = "No match found"
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
                found_string_marked = get_marked_search_result(
                    found_string=found_string
                )

                found_string_extra_chars = text_data[
                    position_end : position_end
                    + SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT
                ]

                section_identifier = SectionIdentifier(
                    section_file_separator=section_file_separator
                )

                self.dialog.content_cls.results_list.add_widget(
                    CustomListItem(
                        text=f"{found_string_marked}{found_string_extra_chars}...",
                        secondary_text=transform_section_name_to_section_text_placeholder(
                            section_name=section_identifier.section_name
                        ),
                        tertiary_text=transform_position_to_position_text_placeholder(
                            position_start=position_start
                        ),
                        on_release=self.execute_goto_search_result,
                    )
                )

        self.dialog.content_cls.search_results_message = (
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
            self.dialog.content_cls.add_section_result_message = "Invalid name"
            return

        section_name = args[0]
        section_identifier = SectionIdentifier(section_name=section_name)

        if section_identifier.section_file_separator in self.file.section_identifiers:
            self.dialog.content_cls.add_section_result_message = "Name already exists"
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

        self.cancel_dialog()

    def execute_goto_external_url(self):
        return webbrowser.open(EXTERNAL_REPOSITORY_URL)

    def execute_sync_login(self):
        pass

    def cancel_dialog(self, *args):
        self.dialog.dismiss()
        self.dialog = MDDialog()

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
        content = ShowFileMetadataDialogContent(
            show_file_metadata_label=self.model.formatted, cancel=self.cancel_dialog,
        )
        self.dialog = MDDialog(
            title="Show File metadata:", type="custom", content_cls=content,
        )
        self.dialog.open()

    def press_menu_item_show_app_metadata(self, *args):
        app_info = linesep.join(APP_METADATA_ROWS)

        content = ShowAppMetadataDialogContent(
            show_app_metadata_label=app_info,
            execute_goto_external_url=self.execute_goto_external_url,
            cancel=self.cancel_dialog,
        )
        self.dialog = MDDialog(
            title="Show App metadata:", type="custom", content_cls=content,
        )
        self.dialog.open()

    def press_menu_item_open_sync_options(self):
        content = ShowFileSyncOptionsDialogContent(
            show_file_sync_options_label=f"supported storage providers: "
            f"{', '.join([provider for provider in SUPPORTED_SYNC_PROVIDERS])}",
            cancel=self.cancel_dialog,
        )
        self.dialog = MDDialog(
            title="Show File sync options:", type="custom", content_cls=content,
        )
        self.dialog.open()

    def press_icon_search(self, *args):
        content = SearchDialogContent(
            get_search_switch_state=self.get_search_switch_state,
            search_switch_callback=self.search_switch_callback,
            search_string_placeholder=self.last_searched_string,
            search_results_message="",
            execute_search=self.execute_search,
            cancel=self.cancel_dialog,
        )

        self.dialog = MDDialog(title="Search:", type="custom", content_cls=content,)

        self.dialog.open()

    def press_add_section(self, *args):
        content = AddSectionDialogContent(
            add_section_result_message="",
            execute_add_section=self.execute_add_section,
            cancel=self.cancel_dialog,
        )
        self.dialog = MDDialog(
            title="Add section:", type="custom", content_cls=content,
        )
        self.dialog.open()

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

    def press_menu_item_open_file(self):
        """
        output manager to the screen
        """
        self.file_manager = self.get_file_manager()
        self.file_manager.show(os.getcwd())
        self.manager_open = True

    def file_manager_select_path(self, path):
        """
        It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file
        """
        self.cancel_file_manager()
        self.execute_open_file(file_path=path)

    def cancel_file_manager(self, *args):
        """
        Called when the user reaches the root of the directory tree.
        """
        self.manager_open = False
        self.file_manager.close()
        #self.file_manager = self.get_file_manager()


Builder.load_file(path.join(path.dirname(__file__), "myscreen.kv"))
