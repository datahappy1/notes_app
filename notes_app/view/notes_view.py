import os
import re
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
from kivymd.uix.textfield import TextInput
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import (
    MDList,
    OneLineAvatarIconListItem,
    ThreeLineListItem,
    IRightBodyTouch,
)
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar

from kivy.base import EventLoop
from kivy.uix.textinput import FL_IS_LINEBREAK

from notes_app import __version__
from notes_app.diff import merge_strings
from notes_app.observer.notes_observer import Observer

from notes_app.color import (
    get_color_by_name,
    get_next_color_by_rgba,
    AVAILABLE_COLORS,
    AVAILABLE_SNACK_BAR_COLORS,
)
from notes_app.file import (
    get_validated_file_path,
    File,
    transform_section_separator_to_section_name,
    transform_section_name_to_section_separator,
    SECTION_FILE_NEW_SECTION_PLACEHOLDER,
    SECTION_FILE_NAME_MINIMAL_CHAR_COUNT,
)
from notes_app.font import get_next_font, AVAILABLE_FONTS
from notes_app.mark import get_marked_text
from notes_app.search import (
    Search,
    validate_search_input,
    SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT,
    SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR,
    SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE,
    transform_section_text_placeholder_to_section_name,
    transform_section_name_to_section_text_placeholder,
    transform_position_text_placeholder_to_position,
    transform_position_to_position_text_placeholder,
)

APP_TITLE = "Notes"
APP_METADATA_ROWS = [
    "A simple notes application",
    "built with Python 3.8 & KivyMD",
    f"version {__version__}",
]
EXTERNAL_REPOSITORY_URL = "https://www.github.com/datahappy1/notes_app/"


class CustomTextInput(TextInput):
    # overriding TextInput.insert_text() with added extra condition and (len(_lines_flags) - 1 >= row + 1)
    # to handle a edge case when external update adds multiple line breaks and results in uncaught index error
    def insert_text(self, substring, from_undo=False):
        """Insert new text at the current cursor position. Override this
        function in order to pre-process text for input validation.
        """
        _lines = self._lines
        _lines_flags = self._lines_flags

        if self.readonly or not substring or not self._lines:
            return

        if isinstance(substring, bytes):
            substring = substring.decode("utf8")

        if self.replace_crlf:
            substring = substring.replace("\r\n", "\n")

        self._hide_handles(EventLoop.window)

        if not from_undo and self.multiline and self.auto_indent and substring == "\n":
            substring = self._auto_indent(substring)

        mode = self.input_filter
        if mode not in (None, "int", "float"):
            substring = mode(substring, from_undo)
            if not substring:
                return

        col, row = self.cursor
        cindex = self.cursor_index()
        text = _lines[row]
        len_str = len(substring)
        new_text = text[:col] + substring + text[col:]
        if mode is not None:
            if mode == "int":
                if not re.match(self._insert_int_pat, new_text):
                    return
            elif mode == "float":
                if not re.match(self._insert_float_pat, new_text):
                    return
        self._set_line_text(row, new_text)

        if (
            len_str > 1
            or substring == "\n"
            or (substring == " " and _lines_flags[row] != FL_IS_LINEBREAK)
            or (
                row + 1 < len(_lines)
                and (len(_lines_flags) - 1 >= row + 1)
                and _lines_flags[row + 1] != FL_IS_LINEBREAK
            )
            or (
                self._get_text_width(new_text, self.tab_width, self._label_cached)
                > (self.width - self.padding[0] - self.padding[2])
            )
        ):
            # Avoid refreshing text on every keystroke.
            # Allows for faster typing of text when the amount of text in
            # TextInput gets large.

            (start, finish, lines, lines_flags, len_lines) = self._get_line_from_cursor(
                row, new_text
            )

            # calling trigger here could lead to wrong cursor positioning
            # and repeating of text when keys are added rapidly in a automated
            # fashion. From Android Keyboard for example.
            self._refresh_text_from_property(
                "insert", start, finish, lines, lines_flags, len_lines
            )

        self.cursor = self.get_cursor_from_index(cindex + len_str)
        # handle undo and redo
        self._set_unredo_insert(cindex, cindex + len_str, substring, from_undo)


class IconsContainer(IRightBodyTouch, MDBoxLayout):
    pass


class ItemDrawer(OneLineAvatarIconListItem):
    id = StringProperty(None)
    text = StringProperty(None)
    edit = ObjectProperty(None)
    delete = ObjectProperty(None)


class ContentNavigationDrawer(MDBoxLayout):
    pass


class DrawerList(ThemableBehavior, MDList):
    pass  # set_color_item causing app crashes hard to reproduce

    # def set_color_item(self, instance_item):
    #     """Called when tap on a menu item.
    #     Set the color of the icon and text for the menu item.
    #     """
    #     for item in self.children:
    #         if item.text_color == self.theme_cls.primary_color:
    #             item.text_color = self.theme_cls.text_color
    #             break
    #     instance_item.text_color = self.theme_cls.primary_color


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


class AddSectionDialogContent(MDBoxLayout):
    add_section_result_message = StringProperty(None)
    execute_add_section = ObjectProperty(None)
    cancel = ObjectProperty(None)


class EditSectionDialogContent(MDBoxLayout):
    old_section_name = StringProperty(None)
    edit_section_result_message = StringProperty(None)
    execute_edit_section = ObjectProperty(None)
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


class MenuSettingsItems(Enum):
    SetNextFont = "Set next font"
    IncreaseFontSize = "Increase font size"
    DecreaseFontSize = "Decrease font size"
    SetNextBackgroundColor = "Set next background color"
    SetNextForegroundColor = "Set next foreground color"
    Save = "Save settings"
    ShowAppInfo = "Show application info"


class NotesView(MDBoxLayout, MDScreen, Observer):
    """"
    A class that implements the visual presentation `NotesModel`.

    """

    settings = ObjectProperty()
    defaults = ObjectProperty()

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

        self.search = Search(defaults=self.defaults)
        self.set_properties_from_settings()

        self.file = File(
            file_path=self.model.file_path,
            controller=self.controller,
            defaults=self.defaults,
        )
        self.current_section = self.file.default_section_separator
        self.filter_data_split_by_section()
        self.set_drawer_items(section_separators=self.file.section_separators_sorted)

    @property
    def is_unsaved_change(self):
        return self.auto_save_text_input_change_counter > 0

    def set_properties_from_settings(self):
        self.text_section_view.font_name = self.settings.font_name
        self.text_section_view.font_size = self.settings.font_size
        self.text_section_view.background_color = get_color_by_name(
            colors_list=AVAILABLE_COLORS, color_name=self.settings.background_color
        ).rgba_value
        self.text_section_view.foreground_color = get_color_by_name(
            colors_list=AVAILABLE_COLORS, color_name=self.settings.foreground_color
        ).rgba_value

    def filter_data_split_by_section(self, section_separator=None):
        section_separator = section_separator or self.current_section

        self.text_section_view.section_file_separator = section_separator

        self.text_section_view.text = self.file.get_section_content(
            section_separator=section_separator
        )

        # setting self.text_section_view.text invokes the on_text event method
        # but changing the section without any actual typing is not an unsaved change
        self.auto_save_text_input_change_counter = 0

        # de-select text to cover edge case when
        # the search result is selected even after the related section is deleted
        self.text_section_view.select_text(0, 0)

        section_name = transform_section_separator_to_section_name(
            defaults=self.defaults, section_separator=section_separator
        )

        self.ids.toolbar.title = f"{APP_TITLE} section: {section_name}"

    def set_drawer_items(self, section_separators):
        self.ids.md_list.clear_widgets()

        for section_separator in section_separators:
            self.ids.md_list.add_widget(
                ItemDrawer(
                    id=section_separator,
                    text=transform_section_separator_to_section_name(
                        defaults=self.defaults, section_separator=section_separator
                    ),
                    on_release=lambda x=f"{section_separator}": self.press_drawer_item_callback(
                        x
                    ),
                    edit=self.press_edit_section,
                    delete=self.press_delete_section,
                )
            )

    def press_drawer_item_callback(self, text_item):
        if self.is_unsaved_change:
            self.save_current_section_to_file()

        self.current_section = text_item.id  # separator
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
        return MDDropdownMenu(caller=self.ids.toolbar, items=menu_items, width_mult=5)

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
        return MDDropdownMenu(caller=self.ids.toolbar, items=menu_items, width_mult=5)

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

        self.menu_storage.dismiss()

    def press_menu_settings_item_callback(self, text_item):
        if text_item == MenuSettingsItems.SetNextFont.value:
            next_font = get_next_font(
                fonts_list=AVAILABLE_FONTS, font_name=self.text_section_view.font_name
            )
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
                colors_list=AVAILABLE_COLORS,
                rgba_value=self.text_section_view.background_color,
                skip_rgba_value=self.text_section_view.foreground_color,
            )
            self.text_section_view.background_color = next_background_color.rgba_value
            self.settings.background_color = next_background_color.name
        elif text_item == MenuSettingsItems.SetNextForegroundColor.value:
            next_foreground_color = get_next_color_by_rgba(
                colors_list=AVAILABLE_COLORS,
                rgba_value=self.text_section_view.foreground_color,
                skip_rgba_value=self.text_section_view.background_color,
            )
            self.text_section_view.foreground_color = next_foreground_color.rgba_value
            self.settings.foreground_color = next_foreground_color.name
        elif text_item == MenuSettingsItems.Save.value:
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
            bg_color=get_color_by_name(
                colors_list=AVAILABLE_SNACK_BAR_COLORS, color_name="success_green"
            ).rgba_value,
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
            bg_color=get_color_by_name(
                colors_list=AVAILABLE_SNACK_BAR_COLORS, color_name="failure_red"
            ).rgba_value,
        )
        self.snackbar.size_hint_x = (
            Window.width - (self.snackbar.snackbar_x * 2)
        ) / Window.width
        self.snackbar.open()

    def execute_open_file(self, file_path):
        if not file_path or not exists(file_path):
            self.show_error_bar(error_message="Invalid file")
            return

        validated_file_path = get_validated_file_path(file_path=file_path)
        if not validated_file_path:
            self.show_error_bar(error_message=f"Cannot open the file {file_path}")
            return

        self.controller.set_file_path(validated_file_path)

        try:
            self.file = File(
                file_path=validated_file_path,
                controller=self.controller,
                defaults=self.defaults,
            )
            self.set_drawer_items(
                section_separators=self.file.section_separators_sorted
            )
            self.filter_data_split_by_section(
                section_separator=self.file.default_section_separator
            )
        except ValueError:
            self.file.delete_all_sections_content()
            self.press_add_section()

    def execute_goto_search_result(self, custom_list_item):
        section_name = transform_section_text_placeholder_to_section_name(
            section_text_placeholder=custom_list_item.secondary_text
        )

        self.current_section = transform_section_name_to_section_separator(
            defaults=self.defaults, section_name=section_name
        )
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
            current_section=self.current_section,
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
                found_string_marked = get_marked_text(
                    text=found_string,
                    highlight_style=SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE,
                    highlight_color=SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR,
                )

                found_string_extra_chars = text_data[
                    position_end : position_end
                    + SEARCH_LIST_ITEM_MATCHED_EXTRA_CHAR_COUNT
                ]

                section_name = transform_section_separator_to_section_name(
                    defaults=self.defaults, section_separator=section_file_separator
                )

                self.dialog.content_cls.results_list.add_widget(
                    CustomListItem(
                        text=f"{found_string_marked}{found_string_extra_chars}...",
                        secondary_text=transform_section_name_to_section_text_placeholder(
                            section_name=section_name
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
        section_name = args[0]

        if (
            not section_name
            or len(section_name) < SECTION_FILE_NAME_MINIMAL_CHAR_COUNT
            or section_name.isspace()
            or section_name
            in [
                transform_section_separator_to_section_name(
                    defaults=self.defaults, section_separator=section_separator
                )
                for section_separator in self.file.section_separators_sorted
            ]
        ):
            self.dialog.content_cls.add_section_result_message = "Invalid name"
            return

        section_separator = transform_section_name_to_section_separator(
            defaults=self.defaults, section_name=section_name
        )

        self.file.set_section_content(
            section_separator=section_separator,
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )

        self.filter_data_split_by_section(section_separator=section_separator)

        self.set_drawer_items(section_separators=self.file.section_separators_sorted)

        self.cancel_dialog()

    def execute_edit_section(self, *args):
        old_section_name, new_section_name = args

        if (
            not new_section_name
            or len(new_section_name) < SECTION_FILE_NAME_MINIMAL_CHAR_COUNT
            or new_section_name.isspace()
            or new_section_name
            in [
                transform_section_separator_to_section_name(
                    defaults=self.defaults, section_separator=section_separator
                )
                for section_separator in self.file.section_separators_sorted
            ]
            or old_section_name == new_section_name
        ):
            self.dialog.content_cls.edit_section_result_message = "Invalid name"
            return

        new_section_separator = transform_section_name_to_section_separator(
            defaults=self.defaults, section_name=new_section_name
        )

        old_section_separator = transform_section_name_to_section_separator(
            defaults=self.defaults, section_name=old_section_name
        )

        self.file.rename_section(
            old_section_separator=old_section_separator,
            new_section_separator=new_section_separator,
        )

        self.filter_data_split_by_section(section_separator=new_section_separator)

        self.set_drawer_items(section_separators=self.file.section_separators_sorted)

        self.current_section = new_section_separator

        self.cancel_dialog()

    def execute_goto_external_url(self):
        return webbrowser.open(EXTERNAL_REPOSITORY_URL)

    def cancel_dialog(self, *args):
        self.dialog.dismiss()
        self.dialog = MDDialog()

    def save_current_section_to_file(self):
        merged_current_section_text_data = None

        try:
            if self.model.external_update:
                self.file.reload()
                try:
                    current_section_text_before = self.file.get_section_content(
                        section_separator=self.text_section_view.section_file_separator
                    )
                # KeyError raised if the current section was removed or renamed by a external update
                except KeyError:
                    # merge_strings prioritizes current_section_text_after over current_section_text_before
                    # so empty string placeholder is set to current_section_text_before
                    current_section_text_before = ""
                    # self.file.reload() will remove the current section separator from self.file.section_separators
                    # in case it was deleted or renamed so the current section identifier is added back
                    self.file.set_section_content(
                        section_separator=self.text_section_view.section_file_separator,
                        section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
                    )

                current_section_text_after = self.text_section_view.text

                merged_current_section_text_data = merge_strings(
                    before=current_section_text_before, after=current_section_text_after
                )

                self.text_section_view.text = merged_current_section_text_data
                # un-focus the TextInput so that the cursor is not offset by the external update
                self.text_section_view.focus = False

                self.set_drawer_items(
                    section_separators=self.file.section_separators_sorted
                )

            self.file.set_section_content(
                section_separator=self.text_section_view.section_file_separator,
                section_content=merged_current_section_text_data
                or self.text_section_view.text,
            )

            raw_text_data = self.file.transform_data_by_sections_to_raw_data_content()

            self.controller.save_file_data(data=raw_text_data)

        except Exception as exc:
            self.show_error_bar(
                error_message=f"Error while saving file, try recovering from dump file, details: {exc}"
            )
            return

    def press_menu_item_save_file(self, *args):
        self.save_current_section_to_file()

    def press_menu_item_show_file_metadata(self, *args):
        content = ShowFileMetadataDialogContent(
            show_file_metadata_label=self.model.formatted, cancel=self.cancel_dialog
        )
        self.dialog = MDDialog(
            title="Show File metadata:", type="custom", content_cls=content
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
            title="Show App metadata:", type="custom", content_cls=content
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

        self.dialog = MDDialog(title="Search:", type="custom", content_cls=content)

        self.dialog.open()

    def press_add_section(self, *args):
        content = AddSectionDialogContent(
            add_section_result_message="",
            execute_add_section=self.execute_add_section,
            cancel=self.cancel_dialog,
        )
        self.dialog = MDDialog(title="Add section:", type="custom", content_cls=content)
        self.dialog.open()

    def press_edit_section(self, section_item):
        section_name = transform_section_separator_to_section_name(
            defaults=self.defaults, section_separator=section_item.id
        )

        content = EditSectionDialogContent(
            old_section_name=section_name,
            edit_section_result_message="",
            execute_edit_section=self.execute_edit_section,
            cancel=self.cancel_dialog,
        )

        self.dialog = MDDialog(
            title=f"Edit section {section_name}:", type="custom", content_cls=content
        )
        self.dialog.open()

    def press_delete_section(self, section_item):
        if len(self.file.section_separators_sorted) == 1:
            self.show_error_bar(error_message="Cannot delete last section")
            return

        self.ids.md_list.remove_widget(section_item)

        section_separator = section_item.id
        self.file.delete_section_content(section_separator=section_separator)

        self.filter_data_split_by_section(
            section_separator=self.file.default_section_separator
        )

    def text_input_changed_callback(self):
        self.auto_save_text_input_change_counter += 1

        if (
            self.auto_save_text_input_change_counter
            == self.defaults.DEFAULT_AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT
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


Builder.load_file(path.join(path.dirname(__file__), "notes_view.kv"))
