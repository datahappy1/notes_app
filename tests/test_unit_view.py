import os
import time
from datetime import datetime, timedelta
from copy import copy
from os import linesep

from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager, FloatButton
from kivymd.uix.menu import MDDropdownMenu

from notes_app.defaults import Defaults
from notes_app.file import (
    File,
    transform_section_name_to_section_separator,
    SECTION_FILE_NEW_SECTION_PLACEHOLDER,
)
from notes_app.search import Search
from notes_app.view.notes_view import (
    DrawerList,
    MenuSettingsItems,
    MenuStorageItems,
    ItemDrawer,
    ShowFileMetadataDialogContent,
    ShowAppMetadataDialogContent,
    CustomSnackbar,
    CustomListItem,
    APP_METADATA_ROWS,
)


class TestView:
    def test_view(self, get_app):
        assert get_app.model
        assert get_app.controller

        screen = get_app.controller.get_screen()

        assert isinstance(screen.menu_storage, MDDropdownMenu)
        assert isinstance(screen.menu_settings, MDDropdownMenu)
        assert screen.last_searched_string == ""

        assert isinstance(screen.file, File)
        assert screen.current_section == screen.file.default_section_separator
        assert isinstance(screen.search, Search)

        assert screen.auto_save_text_input_change_counter == 0
        assert screen.ids.toolbar.title == "Notes section: first"

    def test_is_unsaved_change(self, get_app):
        screen = get_app.controller.get_screen()
        assert screen.is_unsaved_change is False
        screen.text_input_changed_callback()
        assert screen.is_unsaved_change is True

    def test_set_properties_from_settings(self, get_app):
        screen = get_app.controller.get_screen()
        screen.set_properties_from_settings()

        assert screen.text_section_view.font_name == "RobotoMono-Regular"
        assert screen.text_section_view.font_size == 14.0
        assert screen.text_section_view.background_color == [0, 0, 0, 1]
        assert screen.text_section_view.foreground_color == [0, 0.5, 0, 1]

    def test_filter_data_split_by_section(self, get_app):
        screen = get_app.controller.get_screen()
        screen.filter_data_split_by_section()

        assert screen.text_section_view.section_file_separator == "<section=first> "
        assert screen.text_section_view.text == f"Quod equidem non reprehendo\n"
        assert screen.text_section_view.selection_text == ""
        assert screen.ids.toolbar.title == "Notes section: first"

    def test_set_drawer_items(self, get_app):
        screen = get_app.controller.get_screen()

        assert isinstance(screen.ids.md_list, DrawerList)

        children_before = copy(screen.ids.md_list.children)
        assert len(children_before) == 2

        screen.set_drawer_items(
            section_separators=screen.file.section_separators_sorted
        )

        children_after = copy(screen.ids.md_list.children)
        assert len(children_after) == 2
        assert not any(x in children_before for x in children_after)
        assert all(isinstance(x, ItemDrawer) for x in children_after)

    def test_press_drawer_item_callback(self, get_app):
        screen = get_app.controller.get_screen()

        class _TextItem:
            def __init__(self, section_separator):
                self.id = section_separator

        screen.auto_save_text_input_change_counter = 0
        text_item = _TextItem("<section=first> ")
        screen.press_drawer_item_callback(text_item=text_item)

        assert screen.text_section_view.section_file_separator == "<section=first> "
        assert screen.text_section_view.text == f"Quod equidem non reprehendo\n"
        assert screen.auto_save_text_input_change_counter == 0

        screen.auto_save_text_input_change_counter = 2
        text_item = _TextItem("<section=second> ")
        screen.press_drawer_item_callback(text_item=text_item)

        assert screen.text_section_view.section_file_separator == "<section=second> "
        assert screen.text_section_view.text == f"Quis istum dolorem timet"
        assert screen.auto_save_text_input_change_counter == 0

    def test_get_menu_storage(self, get_app):
        screen = get_app.controller.get_screen()
        menu = screen.get_menu_storage()

        assert isinstance(menu.items, list)

        for item in menu.items:
            assert isinstance(item["text"], str)
            assert isinstance(item["viewclass"], str)
            assert callable(item["on_release"])

    def test_get_menu_settings(self, get_app):
        screen = get_app.controller.get_screen()
        menu = screen.get_menu_settings()

        assert isinstance(menu.items, list)

        for item in menu.items:
            assert isinstance(item["text"], str)
            assert isinstance(item["viewclass"], str)
            assert callable(item["on_release"])

    def test_press_menu_storage_item_callback(self, get_app):
        screen = get_app.controller.get_screen()

        value = MenuStorageItems.ChooseFile.value
        screen.press_menu_storage_item_callback(text_item=value)
        assert screen.manager_open is True
        assert isinstance(screen.file_manager, MDFileManager)

        value = MenuStorageItems.ShowFileInfo.value
        screen.press_menu_storage_item_callback(text_item=value)
        assert isinstance(screen.dialog, MDDialog)
        assert screen.dialog.title == "Show File metadata:"
        assert isinstance(screen.dialog.content_cls, ShowFileMetadataDialogContent)

        value = MenuStorageItems.Save.value
        model_change_ts_before = get_app.model.last_updated_on
        screen.press_menu_storage_item_callback(text_item=value)
        assert isinstance(screen.dialog, MDDialog)
        model_change_ts_after = get_app.model.last_updated_on
        assert model_change_ts_after >= model_change_ts_before

    def test_press_menu_settings_item_callback(self, get_app):
        screen = get_app.controller.get_screen()

        # change font name
        assert screen.text_section_view.font_name == "RobotoMono-Regular"
        assert screen.settings.font_name == "RobotoMono-Regular"

        value = MenuSettingsItems.SetNextFont.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.font_name == "Roboto-Bold"
        assert screen.settings.font_name == "Roboto-Bold"

        # increase font size
        assert screen.text_section_view.font_size == 14.0
        assert screen.settings.font_size == "14.0"

        value = MenuSettingsItems.IncreaseFontSize.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.font_size == 16.0
        assert screen.settings.font_size == "16.0"

        # decrease font size
        assert screen.text_section_view.font_size == 16.0
        assert screen.settings.font_size == "16.0"

        value = MenuSettingsItems.DecreaseFontSize.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.font_size == 14.0
        assert screen.settings.font_size == "14.0"

        # change background color
        assert screen.text_section_view.background_color == [0, 0, 0, 1]
        assert screen.settings.background_color == "black"

        value = MenuSettingsItems.SetNextBackgroundColor.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.background_color == [0, 0, 1, 1]
        assert screen.settings.background_color == "blue"

        # change foreground color
        assert screen.text_section_view.foreground_color == [0, 0.5, 0, 1]
        assert screen.settings.foreground_color == "green"

        value = MenuSettingsItems.SetNextForegroundColor.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.foreground_color == [0, 1, 0, 1]
        assert screen.settings.foreground_color == "lime"

        # save settings
        value = MenuSettingsItems.Save.value
        screen.press_menu_settings_item_callback(text_item=value)
        assert get_app.controller.view.settings.font_name == "Roboto-Bold"
        assert get_app.controller.view.settings.font_size == "14.0"
        assert get_app.controller.view.settings.background_color == "blue"
        assert get_app.controller.view.settings.foreground_color == "lime"

        assert get_app.controller.view.settings.store["font_name"] == {
            "value": "Roboto-Bold"
        }
        assert get_app.controller.view.settings.store["font_size"] == {"value": "14.0"}
        assert get_app.controller.view.settings.store["background_color"] == {
            "value": "blue"
        }
        assert get_app.controller.view.settings.store["foreground_color"] == {
            "value": "lime"
        }

        # ShowAppInfo
        value = MenuSettingsItems.ShowAppInfo.value
        screen.press_menu_settings_item_callback(text_item=value)
        assert isinstance(screen.dialog, MDDialog)
        assert screen.dialog.title == "Show App metadata:"
        assert isinstance(screen.dialog.content_cls, ShowAppMetadataDialogContent)

    def test_notify_model_is_changed(self, get_app):
        screen = get_app.controller.get_screen()

        test_data = """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet
"""
        screen.controller.save_file_data(data=test_data)

        assert isinstance(screen.snackbar, CustomSnackbar)
        assert screen.snackbar.text == "changes saved"

    def test_show_error_bar(self, get_app):
        screen = get_app.controller.get_screen()

        section_item = ItemDrawer(
            id="<section=first> ", text="", edit=None, delete=None
        )

        screen.file.set_section_content(
            section_separator="<section=first> ",
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )
        screen.press_delete_section(section_item=section_item)

        section_item = ItemDrawer(
            id="<section=second> ", text="", edit=None, delete=None
        )

        screen.file.set_section_content(
            section_separator="<section=second> ",
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )
        screen.press_delete_section(section_item=section_item)

        assert isinstance(screen.snackbar, CustomSnackbar)
        assert screen.snackbar.text == "Cannot delete last section"

    def test_execute_open_file(self, get_app, get_empty_file_file_path):
        screen = get_app.controller.get_screen()

        assert screen.manager_open is False
        screen.press_menu_item_open_file()
        assert screen.manager_open is True
        assert isinstance(screen.file_manager, MDFileManager)
        assert isinstance(screen.file_manager.children[0], FloatButton)
        assert isinstance(screen.file_manager.children[1], MDBoxLayout)

        # NOTES_FILE_PATH
        screen.execute_open_file(
            file_path=get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME
        )
        assert (
            screen.file._file_path
            == get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME
        )
        assert isinstance(screen.ids.md_list.children[0], ItemDrawer)
        assert screen.ids.md_list.children[0].id == "<section=second> "
        assert screen.text_section_view.text == "Quod equidem non reprehendo\n"

        # EMPTY_NOTES_FILE_PATH
        screen.execute_open_file(file_path=get_empty_file_file_path)
        assert screen.file._data_by_sections == {}

        assert screen.dialog.title == "Add section:"

    def test_execute_goto_search_result(self, get_app):
        screen = get_app.controller.get_screen()

        class _CustomListItem:
            def __init__(self, secondary_text, tertiary_text):
                self.secondary_text = secondary_text
                self.tertiary_text = tertiary_text

        custom_list_item = _CustomListItem("second", "10")

        screen.dialog = MDDialog()

        assert screen.execute_goto_search_result(custom_list_item) is None
        assert screen.text_section_view.cursor == (10, 0)
        # screen.execute_goto_search_result() wraps up by closing the dialog
        assert screen.dialog.title == ""

    def test_get_search_switch_state(self, get_app):
        screen = get_app.controller.get_screen()

        assert (
            screen.get_search_switch_state(switch_id="search_case_sensitive_switch")
            == screen.search.search_case_sensitive
        )

        assert (
            screen.get_search_switch_state(switch_id="search_all_sections_switch")
            == screen.search.search_all_sections
        )

    def test_switch_callback(self, get_app):
        screen = get_app.controller.get_screen()

        screen.search_switch_callback(
            switch_id="search_case_sensitive_switch", state="state1"
        )
        assert screen.search.search_case_sensitive == "state1"

        screen.search_switch_callback(
            switch_id="search_all_sections_switch", state="state2"
        )

        assert screen.search.search_all_sections == "state2"

    def test_execute_search(self, get_app):
        screen = get_app.controller.get_screen()

        class SearchDialogContent(MDBoxLayout):
            get_search_switch_state = ObjectProperty(None)
            switch_callback = ObjectProperty(None)
            search_string_placeholder = StringProperty(None)
            search_results_message = StringProperty(None)
            execute_search = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = SearchDialogContent(
            get_search_switch_state=_,
            switch_callback=_,
            search_string_placeholder="",
            search_results_message="",
            execute_search=_,
            cancel=_,
        )

        screen.dialog = MDDialog(title="test title", content_cls=content)
        screen.dialog.open()

        assert screen.execute_search("") is None
        assert screen.dialog.content_cls.search_results_message == "Invalid search"
        assert screen.dialog.content_cls.results_list.children == []

        assert screen.execute_search(None) is None
        assert screen.dialog.content_cls.search_results_message == "Invalid search"
        assert screen.dialog.content_cls.results_list.children == []

        screen.search.search_all_sections = False
        assert screen.execute_search("lor") is None
        assert screen.dialog.content_cls.search_results_message == "No match found"
        assert screen.dialog.content_cls.results_list.children == []

        screen.search.search_all_sections = True
        assert screen.execute_search("lor") is None
        assert (
            screen.dialog.content_cls.search_results_message
            == "Match on 1 position found"
        )
        assert len(screen.dialog.content_cls.results_list.children) == 1
        assert isinstance(
            screen.dialog.content_cls.results_list.children[0], CustomListItem
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].text
            == f"[b][color=ff0000]lor[/color][/b]em timet..."
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].secondary_text
            == "section second"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].tertiary_text
            == "position 13"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0]
            .on_release.__str__()
            .startswith(
                "<bound method ButtonBehavior.on_release of <notes_app.view.notes_view.CustomListItem object at"
            )
        )

        screen.search.search_case_sensitive = False
        assert screen.execute_search("Quod") is None
        assert (
            screen.dialog.content_cls.search_results_message
            == "Match on 1 position found"
        )
        assert len(screen.dialog.content_cls.results_list.children) == 1
        assert isinstance(
            screen.dialog.content_cls.results_list.children[0], CustomListItem
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].text
            == f"[b][color=ff0000]Quod[/color][/b] equidem non reprehendo\n..."
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].secondary_text
            == "section first"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].tertiary_text
            == "position 0"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0]
            .on_release.__str__()
            .startswith(
                "<bound method ButtonBehavior.on_release of <notes_app.view.notes_view.CustomListItem object at"
            )
        )

        screen.search.search_case_sensitive = True
        assert screen.execute_search("Quod") is None
        assert (
            screen.dialog.content_cls.search_results_message
            == "Match on 1 position found"
        )
        assert len(screen.dialog.content_cls.results_list.children) == 1
        assert isinstance(
            screen.dialog.content_cls.results_list.children[0], CustomListItem
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].text
            == f"[b][color=ff0000]Quod[/color][/b] equidem non reprehendo\n..."
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].secondary_text
            == "section first"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].tertiary_text
            == "position 0"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0]
            .on_release.__str__()
            .startswith(
                "<bound method ButtonBehavior.on_release of <notes_app.view.notes_view.CustomListItem object at"
            )
        )

        screen.search.search_case_sensitive = False
        assert screen.execute_search("Qu") is None
        assert (
            screen.dialog.content_cls.search_results_message
            == "Matches on 3 positions found"
        )
        assert len(screen.dialog.content_cls.results_list.children) == 3

        assert isinstance(
            screen.dialog.content_cls.results_list.children[0], CustomListItem
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].text
            == f"[b][color=ff0000]Qu[/color][/b]is istum dolorem timet..."
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].secondary_text
            == "section second"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0].tertiary_text
            == "position 0"
        )
        assert (
            screen.dialog.content_cls.results_list.children[0]
            .on_release.__str__()
            .startswith(
                "<bound method ButtonBehavior.on_release of <notes_app.view.notes_view.CustomListItem object at"
            )
        )
        assert isinstance(
            screen.dialog.content_cls.results_list.children[1], CustomListItem
        )
        assert (
            screen.dialog.content_cls.results_list.children[1].text
            == f"[b][color=ff0000]qu[/color][/b]idem non reprehendo\n..."
        )
        assert (
            screen.dialog.content_cls.results_list.children[1].secondary_text
            == "section first"
        )
        assert (
            screen.dialog.content_cls.results_list.children[1].tertiary_text
            == "position 6"
        )
        assert (
            screen.dialog.content_cls.results_list.children[1]
            .on_release.__str__()
            .startswith(
                "<bound method ButtonBehavior.on_release of <notes_app.view.notes_view.CustomListItem object at"
            )
        )
        assert isinstance(
            screen.dialog.content_cls.results_list.children[2], CustomListItem
        )
        assert (
            screen.dialog.content_cls.results_list.children[2].text
            == f"[b][color=ff0000]Qu[/color][/b]od equidem non reprehendo\n..."
        )
        assert (
            screen.dialog.content_cls.results_list.children[2].secondary_text
            == "section first"
        )
        assert (
            screen.dialog.content_cls.results_list.children[2].tertiary_text
            == "position 0"
        )
        assert (
            screen.dialog.content_cls.results_list.children[2]
            .on_release.__str__()
            .startswith(
                "<bound method ButtonBehavior.on_release of <notes_app.view.notes_view.CustomListItem object at"
            )
        )

    def test_execute_add_section(self, get_app):
        screen = get_app.controller.get_screen()

        class _AddSectionDialogContent(MDBoxLayout):
            add_section_result_message = StringProperty(None)
            execute_add_section = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = _AddSectionDialogContent(
            add_section_result_message="", execute_add_section=_, cancel=_
        )

        screen.dialog = MDDialog(title="test title", content_cls=content)
        screen.dialog.open()

        section_name = ""
        assert screen.execute_add_section(section_name) is None
        assert screen.dialog.content_cls.add_section_result_message == "Invalid name"

        section_name = None
        assert screen.execute_add_section(section_name) is None
        assert screen.dialog.content_cls.add_section_result_message == "Invalid name"

        # duplicate section name
        section_name = "first"
        assert screen.execute_add_section(section_name) is None
        assert screen.dialog.content_cls.add_section_result_message == "Invalid name"

        section_name = "new section"
        assert len(screen.file.section_separators_sorted) == 2
        assert screen.execute_add_section(section_name) is None

        # add section dialog is closed
        assert screen.dialog.content_cls is None

        assert len(screen.file.section_separators_sorted) == 3
        assert screen.file.section_separators_sorted[1] == "<section=new section> "
        assert (
            screen.file.get_section_content(section_separator="<section=new section> ")
            == ""
        )
        assert (
            screen.text_section_view.section_file_separator == "<section=new section> "
        )
        assert screen.text_section_view.text == f""
        assert screen.ids.toolbar.title == "Notes section: new section"

    def test_execute_edit_section(self, get_app):
        screen = get_app.controller.get_screen()

        class _EditSectionDialogContent(MDBoxLayout):
            edit_section_result_message = StringProperty(None)
            execute_edit_section = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = _EditSectionDialogContent(
            edit_section_result_message="", execute_edit_section=_, cancel=_
        )

        screen.dialog = MDDialog(title="test title", content_cls=content)
        screen.dialog.open()

        old_section_name = ""
        new_section_name = ""
        assert screen.execute_edit_section(old_section_name, new_section_name) is None
        assert screen.dialog.content_cls.edit_section_result_message == "Invalid name"

        old_section_name = None
        new_section_name = ""
        assert screen.execute_edit_section(old_section_name, new_section_name) is None
        assert screen.dialog.content_cls.edit_section_result_message == "Invalid name"

        old_section_name = "first"
        new_section_name = "first"
        assert screen.execute_edit_section(old_section_name, new_section_name) is None
        assert screen.dialog.content_cls.edit_section_result_message == "Invalid name"

        old_section_name = "first"
        new_section_name = "updated section name"
        assert screen.current_section == "<section=first> "
        assert len(screen.file.section_separators_sorted) == 2
        assert screen.execute_edit_section(old_section_name, new_section_name) is None

        # add section dialog is closed
        assert screen.dialog.content_cls is None
        assert screen.current_section == "<section=updated section name> "
        assert len(screen.file.section_separators_sorted) == 2
        assert (
            screen.file.section_separators_sorted[1]
            == "<section=updated section name> "
        )

        assert (
            screen.file.get_section_content(
                section_separator="<section=updated section name> "
            )
            == """Quod equidem non reprehendo
"""
        )
        assert (
            screen.text_section_view.section_file_separator
            == "<section=updated section name> "
        )
        assert (
            screen.text_section_view.text
            == """Quod equidem non reprehendo
"""
        )
        assert screen.ids.toolbar.title == "Notes section: updated section name"

    def test_goto_external_url(self, get_app):
        # opens browser
        # screen = get_app.controller.get_screen()

        # assert screen.execute_goto_external_url()
        pass

    def test_cancel_dialog(self, get_app):
        screen = get_app.controller.get_screen()

        class _AddSectionDialogContent(MDBoxLayout):
            add_section_result_message = StringProperty(None)
            execute_add_section = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = _AddSectionDialogContent(
            add_section_result_message="test message", execute_add_section=_, cancel=_
        )

        screen.dialog = MDDialog(title="test title", content_cls=content)
        screen.dialog.open()

        assert screen.dialog.content_cls.add_section_result_message == "test message"
        _dialog_id_prev = id(screen.dialog)

        assert screen.cancel_dialog() is None
        assert screen.dialog.content_cls is None
        assert _dialog_id_prev != id(screen.dialog)

    def test_save_current_section_to_file_is_not_external_update(self, get_app):
        # setting model._last_updated_on manually will guarantee model.external_update returns False
        get_app.controller.model._last_updated_on = int(time.time())

        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        assert screen.save_current_section_to_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=a> test text"""
        )

    def test_save_current_section_to_file_is_external_update(self, get_app):
        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.file.set_section_content(
            section_separator="<section=a> ",
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        # setting model._last_updated_on manually to the past will guarantee model.external_update returns True
        d = datetime.today() - timedelta(hours=1)
        get_app.controller.model._last_updated_on = int(d.timestamp())

        screen.text_section_view.focus = True

        assert screen.save_current_section_to_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=a> test text"""
        )

        assert screen.text_section_view.focus is False

    def test_save_current_section_to_file_is_external_update_with_changes_to_current_section(
        self, get_app
    ):
        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.file.set_section_content(
            section_separator="<section=a> ",
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        # external update to the current section=a that will be merged
        screen.file._data_by_sections = {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
            "<section=a> ": "test text mod",
        }
        text_data = screen.file.transform_data_by_sections_to_raw_data_content()
        screen.controller.save_file_data(data=text_data)

        # setting model._last_updated_on manually to the past will guarantee model.external_update returns True
        d = datetime.today() - timedelta(hours=1)
        get_app.controller.model._last_updated_on = int(d.timestamp())

        assert screen.save_current_section_to_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=a> test text mod"""
        )

    def test_save_current_section_to_file_is_external_update_delete_current_section(
        self, get_app
    ):
        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.file.set_section_content(
            section_separator="<section=a> ",
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        # external delete of the current section=a that will be recovered during the merge
        screen.file._data_by_sections = {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }
        text_data = screen.file.transform_data_by_sections_to_raw_data_content()
        screen.controller.save_file_data(data=text_data)

        # setting model._last_updated_on manually to the past will guarantee model.external_update returns True
        d = datetime.today() - timedelta(hours=1)
        get_app.controller.model._last_updated_on = int(d.timestamp())

        assert screen.save_current_section_to_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=a> test text"""
        )

    def test_save_current_section_to_file_is_external_update_with_changes_to_different_section(
        self, get_app
    ):
        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.text_section_view.section_file_separator = "<section=first> "

        # external update
        screen.file._data_by_sections = {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
            "<section=test> ": "test data",
        }
        text_data = screen.file.transform_data_by_sections_to_raw_data_content()
        screen.controller.save_file_data(data=text_data)

        # setting model._last_updated_on manually to the past will guarantee model.external_update returns True
        d = datetime.today() - timedelta(hours=1)
        get_app.controller.model._last_updated_on = int(d.timestamp())

        assert screen.save_current_section_to_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=test> test data"""
        )

    def test_save_current_section_to_file_handle_error(self, get_app):
        # setting model._last_updated_on manually will guarantee model.external_update returns False
        get_app.controller.model._last_updated_on = int(time.time())

        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        # setting model file path as empty string is invalid enough to raise file write error exc
        get_app.controller.model.file_path = ""

        assert screen.save_current_section_to_file() is None

        # assert `<section=a> test text` was not added to the file,
        # however the file content still contains data before the write failure
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        assert isinstance(screen.snackbar, CustomSnackbar)
        assert screen.snackbar.text.startswith("Error while saving file, try recovering from dump file, details:")

    def test_press_menu_item_save_file_is_not_external_update(self, get_app):
        # setting model._last_updated_on manually will guarantee model.external_update returns False
        get_app.controller.model._last_updated_on = int(time.time())

        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        assert screen.press_menu_item_save_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=a> test text"""
        )

    def test_press_menu_item_save_file_is_external_update(self, get_app):
        # setting model._last_updated_on manually to the past will guarantee model.external_update returns True
        d = datetime.today() - timedelta(hours=1)
        get_app.controller.model._last_updated_on = int(d.timestamp())

        screen = get_app.controller.get_screen()

        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        )

        screen.file.set_section_content(
            section_separator="<section=a> ",
            section_content=SECTION_FILE_NEW_SECTION_PLACEHOLDER,
        )

        screen.text_section_view.section_file_separator = "<section=a> "

        screen.text_section_view.text = "test text"

        assert screen.press_menu_item_save_file() is None
        assert (
            screen.file.get_raw_data_content()
            == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet<section=a> test text"""
        )

    def test_press_menu_item_show_file_metadata(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.press_menu_item_show_file_metadata() is None

        assert isinstance(screen.dialog.content_cls.show_file_metadata_label, str)
        assert len(screen.dialog.content_cls.show_file_metadata_label.splitlines()) == 3

    def test_press_menu_item_show_app_metadata(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.press_menu_item_show_app_metadata() is None

        assert screen.dialog.content_cls.show_app_metadata_label == linesep.join(
            APP_METADATA_ROWS
        )

    def test_press_icon_search(self, get_app):
        screen = get_app.controller.get_screen()

        screen.last_searched_string = "test placeholder"
        screen.press_icon_search()

        assert screen.dialog.content_cls.get_search_switch_state.__str__().startswith(
            "<bound method NotesView.get_search_switch_state of <Screen name=''>>"
        )
        assert screen.dialog.content_cls.search_switch_callback.__str__().startswith(
            "<bound method NotesView.search_switch_callback of <Screen name=''>>"
        )
        assert screen.dialog.content_cls.search_string_placeholder == "test placeholder"
        assert screen.dialog.content_cls.search_results_message == ""
        assert screen.dialog.content_cls.execute_search.__str__().startswith(
            "<bound method NotesView.execute_search of <Screen name=''>>"
        )
        assert screen.dialog.content_cls.cancel.__str__().startswith(
            "<bound method NotesView.cancel_dialog of <Screen name=''>>"
        )

    def test_press_add_section(self, get_app):
        screen = get_app.controller.get_screen()

        screen.press_add_section()

        assert screen.dialog.content_cls.add_section_result_message == ""
        assert screen.dialog.content_cls.execute_add_section.__str__().startswith(
            "<bound method NotesView.execute_add_section of <Screen name=''>>"
        )
        assert screen.dialog.content_cls.cancel.__str__().startswith(
            "<bound method NotesView.cancel_dialog of <Screen name=''>>"
        )

    def test_press_edit_section(self, get_app):
        screen = get_app.controller.get_screen()

        screen.press_edit_section(
            section_item=ItemDrawer(
                id="<section=first> ", text="", edit=None, delete=None
            )
        )

        assert screen.dialog.content_cls.edit_section_result_message == ""
        assert screen.dialog.content_cls.execute_edit_section.__str__().startswith(
            "<bound method NotesView.execute_edit_section of <Screen name=''>>"
        )
        assert screen.dialog.content_cls.cancel.__str__().startswith(
            "<bound method NotesView.cancel_dialog of <Screen name=''>>"
        )

    def test_press_delete_section(self, get_app):
        screen = get_app.controller.get_screen()

        section_item = screen.ids.md_list.children[0]

        assert len(screen.ids.md_list.children) == 2

        assert screen.file._data_by_sections == {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }

        defaults = Defaults()

        screen.filter_data_split_by_section(
            section_separator=transform_section_name_to_section_separator(
                defaults=defaults, section_name="second"
            )
        )

        assert screen.press_delete_section(section_item=section_item) is None

        assert len(screen.ids.md_list.children) == 1

        assert screen.file.section_separators_sorted[0] == "<section=first> "

        assert screen.file._data_by_sections == {
            "<section=first> ": "Quod equidem non reprehendo\n"
        }

        section_item = screen.ids.md_list.children[0]
        assert screen.press_delete_section(section_item=section_item) is None
        assert screen.snackbar.text == "Cannot delete last section"

    def test_text_input_changed_callback_is_external_update(self, get_app):
        # setting model._last_updated_on manually to the past will guarantee model.external_update returns True
        d = datetime.today() - timedelta(hours=1)
        get_app.controller.model._last_updated_on = int(d.timestamp())

        screen = get_app.controller.get_screen()

        screen.auto_save_text_input_change_counter = (
            get_app.controller.defaults.DEFAULT_AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT - 1
        )

        # external update
        screen.file._data_by_sections = {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
            "<section=test>": "test data",
        }

        text_data = screen.file.transform_data_by_sections_to_raw_data_content()
        screen.controller.save_file_data(data=text_data)

        assert screen.text_input_changed_callback() is None
        assert screen.auto_save_text_input_change_counter == 0

        assert (
            screen.controller.read_file_data()
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet<section=test>test data"""
        )

        assert screen.text_input_changed_callback() is None
        assert screen.auto_save_text_input_change_counter == 1

    def test_text_input_changed_callback_is_not_external_update(self, get_app):
        # setting model._last_updated_on manually will guarantee model.external_update returns False
        get_app.controller.model._last_updated_on = int(time.time())

        screen = get_app.controller.get_screen()

        screen.auto_save_text_input_change_counter = (
            get_app.controller.defaults.DEFAULT_AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT - 1
        )

        screen.file._data_by_sections = {
            "<section=first> ": "Quod equidem non reprehendo\n",
            "<section=second> ": "Quis istum dolorem timet",
        }
        assert screen.text_input_changed_callback() is None
        assert screen.auto_save_text_input_change_counter == 0

        assert (
            screen.controller.read_file_data()
            == """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""
        )

        assert screen.text_input_changed_callback() is None
        assert screen.auto_save_text_input_change_counter == 1

    def test_press_menu_item_open_file(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.press_menu_item_open_file() is None
        assert isinstance(screen.file_manager, MDFileManager)
        assert screen.manager_open is True

    def test_file_manager_select_path(self, get_app):
        screen = get_app.controller.get_screen()

        screen.file_manager = screen.get_file_manager()
        screen.file_manager.show(os.getcwd())
        screen.manager_open = True

        screen.file_manager_select_path(
            path=get_app.controller.defaults.DEFAULT_NOTES_FILE_NAME
        )
        assert screen.manager_open is False
        assert isinstance(screen.file_manager, MDFileManager)
        assert isinstance(screen.file_manager.children[0], FloatButton)
        assert isinstance(screen.file_manager.children[1], MDBoxLayout)

    def test_cancel_file_manager(self, get_app):
        screen = get_app.controller.get_screen()

        screen.file_manager = screen.get_file_manager()
        screen.file_manager.show(os.getcwd())
        screen.manager_open = True

        screen.cancel_file_manager()
        assert screen.manager_open is False
