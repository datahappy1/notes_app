import os


class Defaults:
    def __init__(self, base_file_path=""):
        self.BASE_FILE_PATH = base_file_path
        self.DEFAULT_MODEL_STORE_FILE_NAME = os.path.join(self.BASE_FILE_PATH, "file_metadata.json")
        self.DEFAULT_NOTES_FILE_NAME = os.path.join(self.BASE_FILE_PATH, "my_first_file.txt")
        self.DEFAULT_SECTION_FILE_SEPARATOR = "<section={name}> "
        self.DEFAULT_SECTION_FILE_SEPARATOR_REGEX = "<section=[a-z A-Z0-9_-]+> "
        self.DEFAULT_SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX = "<section=(.+?)> "
        self.DEFAULT_NOTES_FILE_CONTENT = f"{self.DEFAULT_SECTION_FILE_SEPARATOR.format(name='first')} Your first section. Here you can write your notes."
        self.DEFAULT_AUTO_SAVE_TEXT_INPUT_CHANGE_COUNT = 5
        self.DEFAULT_VALUE_SEARCH_CASE_SENSITIVE = False
        self.DEFAULT_VALUE_SEARCH_ALL_SECTIONS = False
        self.DEFAULT_VALUE_SEARCH_FULL_WORDS = False
        self.DEFAULT_SETTINGS_STORE_FILE_NAME = os.path.join(self.BASE_FILE_PATH, "settings.json")
        self.DEFAULT_SETTINGS_VALUE_FONT_NAME = "RobotoMono-Regular"
        self.DEFAULT_SETTINGS_VALUE_FONT_SIZE = "14.0"
        self.DEFAULT_SETTINGS_VALUE_BACKGROUND_COLOR = "black"
        self.DEFAULT_SETTINGS_VALUE_FOREGROUND_COLOR = "green"
