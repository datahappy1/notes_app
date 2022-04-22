from copy import copy
from os import sep
import pytest
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel
from notes_app.settings import Settings
from notes_app.utils.file import File
from notes_app.utils.search import Search
from notes_app.view.myscreen import DrawerList, MenuSettingsItems, MenuStorageItems, ItemDrawer

settings = Settings()


@pytest.fixture
def get_app():
    class NotesApp(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = MyScreenModel()
            self.controller = MyScreenController(settings=settings, model=self.model)

    return NotesApp()


class TestView:
    def test_view(self, get_app):
        assert get_app.model
        assert get_app.controller

        # raw_file_data = get_app.controller.read_file_data()
        # print(raw_file_data)
        screen = get_app.controller.get_screen()

        assert isinstance(screen.menu_storage, MDDropdownMenu)
        assert isinstance(screen.menu_settings, MDDropdownMenu)
        assert screen.last_searched_string == ""

        assert isinstance(screen.file, File)
        assert screen.current_section_identifier == screen.file.default_section_identifier
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
        assert screen.text_section_view.font_size == 11.0
        assert screen.text_section_view.background_color == [0, 0, 0, 1]
        assert screen.text_section_view.foreground_color == [0.75, 0.75, 0.75, 1]

    def test_filter_data_split_by_section(self, get_app):
        screen = get_app.controller.get_screen()
        screen.filter_data_split_by_section()

        assert screen.text_section_view.section_file_separator == "<section=first> "
        assert screen.text_section_view.text == f"Quod equidem non reprehendo\n"

    def test_set_drawer_items(self, get_app):
        screen = get_app.controller.get_screen()

        assert isinstance(screen.ids.md_list, DrawerList)

        children_before = copy(screen.ids.md_list.children)
        assert len(children_before) == 2

        screen.set_drawer_items(section_identifiers=screen.file.section_identifiers)

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
        assert screen.text_section_view.text == f"Quis istum dolorem timet\n"
        assert screen.auto_save_text_input_change_counter == 0

    def test_get_menu_storage(self, get_app):
        screen = get_app.controller.get_screen()
        menu = screen.get_menu_storage()
        assert menu.items == []
