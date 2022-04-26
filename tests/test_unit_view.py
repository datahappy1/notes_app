from copy import copy
from os import getcwd, linesep

import pytest
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel
from notes_app.settings import Settings
from notes_app.utils.file import File, SectionIdentifier
from notes_app.utils.search import Search
from notes_app.view.myscreen import DrawerList, MenuSettingsItems, MenuStorageItems, ItemDrawer, \
    ShowFileMetadataPopup, ShowAppMetadataPopup, CustomSnackbar, CustomListItem, APP_METADATA_ROWS, \
    AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT

settings = Settings()

SETTINGS_FILE_PATH = f"{getcwd()}/settings.conf"
MODEL_FILE_PATH = f"{getcwd()}/model/myscreen.model"
NOTES_FILE_PATH = f"{getcwd()}/assets/sample.txt"
EMPTY_NOTES_FILE_PATH = f"{getcwd()}/assets/sample_empty.txt"


def set_clean_test_class_state():
    def _write_settings_file():
        with open(file=SETTINGS_FILE_PATH, mode="w") as settings_file:
            settings_file.write(
                "\n".join(["[general_settings]",
                           "font_name = RobotoMono-Regular",
                           "font_size = 11.0",
                           "background_color = black",
                           "foreground_color = silver"])
            )

    _write_settings_file()


def set_clean_test_state():
    def _write_notes_file():
        with open(file=NOTES_FILE_PATH, mode="w") as notes_file:
            notes_file.write(
                "\n".join(["<section=first> Quod equidem non reprehendo",
                           "<section=second> Quis istum dolorem timet"])
            )

    def _write_model_file():
        with open(file=MODEL_FILE_PATH, mode="wb") as model_file:
            model_file.write(
                b"""eyJfZmlsZV9wYXRoIjogIkM6XFxVc2Vyc1xccGF2ZWwucHJ1ZGt5XFxQeWNoYXJtUHJvamVjdHNc
    XG5vdGVzX2FwcFxcdGVzdHMvYXNzZXRzL3NhbXBsZS50eHQiLCAiX2ZpbGVfc2l6ZSI6IDY5LCAi
    X2xhc3RfdXBkYXRlZF9vbiI6ICIyMDIyLTA0LTI2IDEwOjQ1OjU3In0="""
            )

    _write_notes_file()
    _write_model_file()


@pytest.fixture
def get_app():
    class NotesApp(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = MyScreenModel()
            self.controller = MyScreenController(settings=settings, model=self.model)

    return NotesApp()


@pytest.fixture(autouse=True)
def get_fresh_notes_file_content():
    set_clean_test_state()
    yield
    set_clean_test_state()


class TestView:
    def setup_method(self, test_method):
        set_clean_test_class_state()

    def teardown_method(self, test_method):
        set_clean_test_class_state()

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
        assert screen.ids.toolbar.title == "Notes section: first"

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
        assert isinstance(screen.popup, Popup)
        assert screen.popup.title == "Open File"

        value = MenuStorageItems.ShowFileInfo.value
        screen.press_menu_storage_item_callback(text_item=value)
        assert isinstance(screen.popup, Popup)
        assert screen.popup.title == "Show File metadata"
        assert isinstance(screen.popup.content, ShowFileMetadataPopup)

        value = MenuStorageItems.Save.value
        model_change_ts_before = get_app.model.last_updated_on
        screen.press_menu_storage_item_callback(text_item=value)
        assert isinstance(screen.popup, Popup)
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
        assert screen.text_section_view.font_size == 11.0
        assert screen.settings.font_size == "11.0"

        value = MenuSettingsItems.IncreaseFontSize.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.font_size == 13.0
        assert screen.settings.font_size == "13.0"

        # decrease font size
        assert screen.text_section_view.font_size == 13.0
        assert screen.settings.font_size == "13.0"

        value = MenuSettingsItems.DecreaseFontSize.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.font_size == 11.0
        assert screen.settings.font_size == "11.0"

        # change background color
        assert screen.text_section_view.background_color == [0, 0, 0, 1]
        assert screen.settings.background_color == "black"

        value = MenuSettingsItems.SetNextBackgroundColor.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.background_color == [0, 0, 1, 1]
        assert screen.settings.background_color == "blue"

        # change foreground color
        assert screen.text_section_view.foreground_color == [0.75, 0.75, 0.75, 1]
        assert screen.settings.foreground_color == "silver"

        value = MenuSettingsItems.SetNextForegroundColor.value
        screen.press_menu_settings_item_callback(text_item=value)
        screen.press_menu_settings_item_callback(text_item=value)

        assert screen.text_section_view.foreground_color == [1, 0, 1, 1]
        assert screen.settings.foreground_color == "fuchsia"

        # save settings
        value = MenuSettingsItems.SaveSettings.value
        screen.press_menu_settings_item_callback(text_item=value)

        # ShowAppInfo
        value = MenuSettingsItems.ShowAppInfo.value
        screen.press_menu_settings_item_callback(text_item=value)
        assert isinstance(screen.popup, Popup)
        assert screen.popup.title == "Show App metadata"
        assert isinstance(screen.popup.content, ShowAppMetadataPopup)

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

        section_item = ItemDrawer(id="<section=first> ")

        screen.file.delete_all_section_identifiers()
        screen.file.add_section_identifier(section_file_separator="<section=first> ")
        screen.press_delete_section(section_item=section_item)

        assert isinstance(screen.snackbar, CustomSnackbar)
        assert screen.snackbar.text == "Cannot delete last section"

    def test_execute_open_file(self, get_app):
        screen = get_app.controller.get_screen()

        screen.press_menu_item_open_file()
        assert screen.popup.title == "Open File"

        # NOTES_FILE_PATH
        screen.execute_open_file(path=None, filename=(NOTES_FILE_PATH,))
        assert screen.popup.title == "No title"

        assert screen.file._file_path == NOTES_FILE_PATH
        assert isinstance(screen.ids.md_list.children[0], ItemDrawer)
        assert screen.ids.md_list.children[0].id == "<section=second> "
        assert screen.text_section_view.text == "Quod equidem non reprehendo\n"

        # EMPTY_NOTES_FILE_PATH
        screen.execute_open_file(path=None, filename=(EMPTY_NOTES_FILE_PATH,))
        assert screen.file._section_identifiers == []
        assert screen.file._data_by_sections == {}

        assert screen.popup.title == "Add section"

    def test_execute_goto_search_result(self, get_app):
        screen = get_app.controller.get_screen()

        class _CustomListItem:
            def __init__(self, secondary_text, tertiary_text):
                self.secondary_text = secondary_text
                self.tertiary_text = tertiary_text

        custom_list_item = _CustomListItem("second", "10")

        screen.popup = Popup()

        assert screen.execute_goto_search_result(custom_list_item) is None
        assert screen.text_section_view.cursor == (10, 0)
        assert screen.popup.title == "No title"

    def test_get_search_switch_state(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.get_search_switch_state(switch_id="search_case_sensitive_switch") == \
               screen.search.search_case_sensitive

        assert screen.get_search_switch_state(switch_id="search_all_sections_switch") == \
               screen.search.search_all_sections

    def test_switch_callback(self, get_app):
        screen = get_app.controller.get_screen()

        screen.switch_callback(
            switch_id="search_case_sensitive_switch",
            state="state1"
        )
        assert screen.search.search_case_sensitive == "state1"

        screen.switch_callback(
            switch_id="search_all_sections_switch",
            state="state2"
        )

        assert screen.search.search_all_sections == "state2"

    def test_execute_search(self, get_app):
        screen = get_app.controller.get_screen()

        class SearchPopup(FloatLayout):
            get_search_switch_state = ObjectProperty(None)
            switch_callback = ObjectProperty(None)
            search_string_placeholder = StringProperty(None)
            search_results_message = StringProperty(None)
            execute_search = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = SearchPopup(
            get_search_switch_state=_,
            switch_callback=_,
            search_string_placeholder="",
            search_results_message="",
            execute_search=_,
            cancel=_
        )

        screen.popup = Popup(
            title="test title",
            content=content,
        )
        screen.popup.open()

        assert screen.execute_search("") is None
        assert screen.popup.content.search_results_message == "Invalid search"
        assert screen.popup.content.results_list.children == []

        assert screen.execute_search(None) is None
        assert screen.popup.content.search_results_message == "Invalid search"
        assert screen.popup.content.results_list.children == []

        screen.search.search_all_sections = False
        assert screen.execute_search("lor") is None
        assert screen.popup.content.search_results_message == "No match found"
        assert screen.popup.content.results_list.children == []

        screen.search.search_all_sections = True
        assert screen.execute_search("lor") is None
        assert screen.popup.content.search_results_message == "Match on 1 position found"
        assert len(screen.popup.content.results_list.children) == 1
        assert isinstance(screen.popup.content.results_list.children[0], CustomListItem)
        assert screen.popup.content.results_list.children[0].text == f"[b][color=ff0000]lor[/color][/b]em timet..."
        assert screen.popup.content.results_list.children[0].secondary_text == "section second"
        assert screen.popup.content.results_list.children[0].tertiary_text == "position 13"
        assert screen.popup.content.results_list.children[0].on_release.__str__().startswith(
            "<bound method ButtonBehavior.on_release of <notes_app.view.myscreen.CustomListItem object at"
        )

        screen.search.search_case_sensitive = False
        assert screen.execute_search("Quod") is None
        assert screen.popup.content.search_results_message == "Match on 1 position found"
        assert len(screen.popup.content.results_list.children) == 1
        assert isinstance(screen.popup.content.results_list.children[0], CustomListItem)
        assert screen.popup.content.results_list.children[0].text == \
               f"[b][color=ff0000]Quod[/color][/b] equidem non reprehendo\n..."
        assert screen.popup.content.results_list.children[0].secondary_text == "section first"
        assert screen.popup.content.results_list.children[0].tertiary_text == "position 0"
        assert screen.popup.content.results_list.children[0].on_release.__str__().startswith(
            "<bound method ButtonBehavior.on_release of <notes_app.view.myscreen.CustomListItem object at"
        )

        screen.search.search_case_sensitive = True
        assert screen.execute_search("Quod") is None
        assert screen.popup.content.search_results_message == "Match on 1 position found"
        assert len(screen.popup.content.results_list.children) == 1
        assert isinstance(screen.popup.content.results_list.children[0], CustomListItem)
        assert screen.popup.content.results_list.children[0].text == \
               f"[b][color=ff0000]Quod[/color][/b] equidem non reprehendo\n..."
        assert screen.popup.content.results_list.children[0].secondary_text == "section first"
        assert screen.popup.content.results_list.children[0].tertiary_text == "position 0"
        assert screen.popup.content.results_list.children[0].on_release.__str__().startswith(
            "<bound method ButtonBehavior.on_release of <notes_app.view.myscreen.CustomListItem object at"
        )

        screen.search.search_case_sensitive = False
        assert screen.execute_search("Qu") is None
        assert screen.popup.content.search_results_message == "Matches on 3 positions found"
        assert len(screen.popup.content.results_list.children) == 3

        assert isinstance(screen.popup.content.results_list.children[0], CustomListItem)
        assert screen.popup.content.results_list.children[0].text == \
               f"[b][color=ff0000]Qu[/color][/b]is istum dolorem timet..."
        assert screen.popup.content.results_list.children[0].secondary_text == "section second"
        assert screen.popup.content.results_list.children[0].tertiary_text == "position 0"
        assert screen.popup.content.results_list.children[0].on_release.__str__().startswith(
            "<bound method ButtonBehavior.on_release of <notes_app.view.myscreen.CustomListItem object at"
        )
        assert isinstance(screen.popup.content.results_list.children[1], CustomListItem)
        assert screen.popup.content.results_list.children[1].text == \
               f"[b][color=ff0000]qu[/color][/b]idem non reprehendo\n..."
        assert screen.popup.content.results_list.children[1].secondary_text == "section first"
        assert screen.popup.content.results_list.children[1].tertiary_text == "position 6"
        assert screen.popup.content.results_list.children[1].on_release.__str__().startswith(
            "<bound method ButtonBehavior.on_release of <notes_app.view.myscreen.CustomListItem object at"
        )
        assert isinstance(screen.popup.content.results_list.children[2], CustomListItem)
        assert screen.popup.content.results_list.children[2].text == \
               f"[b][color=ff0000]Qu[/color][/b]od equidem non reprehendo\n..."
        assert screen.popup.content.results_list.children[2].secondary_text == "section first"
        assert screen.popup.content.results_list.children[2].tertiary_text == "position 0"
        assert screen.popup.content.results_list.children[2].on_release.__str__().startswith(
            "<bound method ButtonBehavior.on_release of <notes_app.view.myscreen.CustomListItem object at"
        )

    def test_execute_add_section(self, get_app):
        screen = get_app.controller.get_screen()

        class _AddSectionPopup(FloatLayout):
            add_section_result_message = StringProperty(None)
            execute_add_section = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = _AddSectionPopup(
            add_section_result_message="",
            execute_add_section=_,
            cancel=_
        )

        screen.popup = Popup(
            title="test title",
            content=content,
        )
        screen.popup.open()

        section_name = ""
        assert screen.execute_add_section(section_name) is None
        assert screen.popup.content.add_section_result_message == "Invalid name"

        section_name = None
        assert screen.execute_add_section(section_name) is None
        assert screen.popup.content.add_section_result_message == "Invalid name"

        section_name = "first"
        assert screen.execute_add_section(section_name) is None
        assert screen.popup.content is None

        section_name = "new section"
        assert len(screen.file.section_identifiers) == 3
        assert screen.execute_add_section(section_name) is None
        assert len(screen.file.section_identifiers) == 4
        assert screen.file.section_identifiers[3].section_file_separator == "<section=new section> "
        assert screen.file.section_identifiers[3].section_name == "new section"
        assert screen.file.get_section_content(section_file_separator="<section=new section> ") == ""
        assert screen.text_section_view.section_file_separator == "<section=new section> "
        assert screen.text_section_view.text == f""
        assert screen.ids.toolbar.title == "Notes section: new section"

    def test_goto_external_url(self, get_app):
        # opens browser
        # screen = get_app.controller.get_screen()

        # assert screen.execute_goto_external_url()
        pass

    def test_cancel_popup(self, get_app):
        screen = get_app.controller.get_screen()

        class _AddSectionPopup(FloatLayout):
            add_section_result_message = StringProperty(None)
            execute_add_section = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = _AddSectionPopup(
            add_section_result_message="test message",
            execute_add_section=_,
            cancel=_
        )

        screen.popup = Popup(
            title="test title",
            content=content,
        )
        screen.popup.open()

        assert screen.popup.content.add_section_result_message == "test message"

        assert screen.cancel_popup() is None
        assert screen.popup.content is None

    def test_press_menu_item_open_file(self, get_app):
        screen = get_app.controller.get_screen()

        class _OpenFilePopup(FloatLayout):
            open_file = ObjectProperty(None)
            cancel = ObjectProperty(None)

        def _(*args):
            return True

        content = _OpenFilePopup(
            open_file=_, cancel=_
        )
        self.popup = Popup(
            title="Open File",
            content=content,
        )

        assert screen.press_menu_item_open_file() is None

        assert screen.popup.content.open_file.__str__().startswith(
            "<bound method MyScreenView.execute_open_file of <Screen name=''>>"
        )

    def test_save_current_section_to_file(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.file.get_raw_data_content() \
               == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        screen.text_section_view.text = "test text"

        assert screen.save_current_section_to_file() is None
        assert screen.file.get_raw_data_content() \
               == """<section=first> test text<section=second> Quis istum dolorem timet"""

    def test_press_menu_item_save_file(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.file.get_raw_data_content() \
               == """<section=first> Quod equidem non reprehendo\n<section=second> Quis istum dolorem timet"""
        screen.text_section_view.text = "test text"

        assert screen.press_menu_item_save_file() is None
        assert screen.file.get_raw_data_content() \
               == """<section=first> test text<section=second> Quis istum dolorem timet"""

    def test_press_menu_item_show_file_metadata(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.press_menu_item_show_file_metadata() is None

        assert screen.popup.content.show_file_metadata_label == \
               """File path : {cwd}/assets/sample.txt\r
File size (bytes) : 86\r
Last updated on : {dt_now}""".format(cwd=getcwd(), dt_now=screen.model.last_updated_on)

    def test_press_menu_item_show_app_metadata(self, get_app):
        screen = get_app.controller.get_screen()

        assert screen.press_menu_item_show_app_metadata() is None

        assert screen.popup.content.show_app_metadata_label == \
               linesep.join(APP_METADATA_ROWS)

    def test_press_icon_search(self, get_app):
        screen = get_app.controller.get_screen()

        screen.last_searched_string = "test placeholder"
        screen.press_icon_search()

        assert screen.popup.content.get_search_switch_state.__str__().startswith(
            "<bound method MyScreenView.get_search_switch_state of <Screen name=''>>"
        )
        assert screen.popup.content.switch_callback.__str__().startswith(
            "<bound method MyScreenView.switch_callback of <Screen name=''>>"
        )
        assert screen.popup.content.search_string_placeholder == "test placeholder"
        assert screen.popup.content.search_results_message == ""
        assert screen.popup.content.execute_search.__str__().startswith(
            "<bound method MyScreenView.execute_search of <Screen name=''>>"
        )
        assert screen.popup.content.cancel.__str__().startswith(
            "<bound method MyScreenView.cancel_popup of <Screen name=''>>"
        )

    def test_press_add_section(self, get_app):
        screen = get_app.controller.get_screen()

        screen.press_add_section()

        assert screen.popup.content.add_section_result_message == ""
        assert screen.popup.content.execute_add_section.__str__().startswith(
            "<bound method MyScreenView.execute_add_section of <Screen name=''>>"
        )
        assert screen.popup.content.cancel.__str__().startswith(
            "<bound method MyScreenView.cancel_popup of <Screen name=''>>"
        )

    def test_press_delete_section(self, get_app):
        screen = get_app.controller.get_screen()

        section_item = screen.ids.md_list.children[0]

        assert len(screen.ids.md_list.children) == 2

        assert screen.file._data_by_sections == \
               {'<section=first> ': 'Quod equidem non reprehendo\n',
                '<section=second> ': 'Quis istum dolorem timet'}

        screen.filter_data_split_by_section(
            section_identifier=SectionIdentifier(section_name="second")
        )

        assert screen.press_delete_section(section_item=section_item) is None

        assert len(screen.ids.md_list.children) == 1

        assert screen.file.section_identifiers[0].section_name == "first"
        assert screen.file.section_identifiers[0].section_file_separator == "<section=first> "
        assert screen.file._data_by_sections == {'<section=first> ': 'Quod equidem non reprehendo\n'}

        section_item = screen.ids.md_list.children[0]
        assert screen.press_delete_section(section_item=section_item) is None
        assert screen.snackbar.text == "Cannot delete last section"

    def test_text_input_changed_callback(self, get_app):
        screen = get_app.controller.get_screen()

        screen.auto_save_text_input_change_counter = AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT - 1

        screen.file._data_by_sections = {"<section=test> ": "test data"}
        assert screen.text_input_changed_callback() is None
        assert screen.auto_save_text_input_change_counter == 0
        assert screen.controller.read_file_data() == \
               "<section=test> test data<section=first> Quod equidem non reprehendo\n"

        assert screen.text_input_changed_callback() is None
        assert screen.auto_save_text_input_change_counter == 1