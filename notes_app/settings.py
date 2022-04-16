from configparser import ConfigParser
from os import getcwd

FALLBACK_NOTES_FILE_PATH = f"{getcwd()}/assets/sample.txt"
SETTINGS_FILE_PATH = f"{getcwd()}/settings.conf"
GENERAL_SETTINGS_SECTION_NAME = "general_settings"


class Settings:
    def __init__(self):
        self._parser = ConfigParser()
        self._parser.read(SETTINGS_FILE_PATH)

    @property
    def notes_file_path(self):
        return self._parser[GENERAL_SETTINGS_SECTION_NAME]["notes_file_path"]

    @notes_file_path.setter
    def notes_file_path(self, value):
        self._parser[GENERAL_SETTINGS_SECTION_NAME]["notes_file_path"] = str(value)

    @property
    def font_name(self):
        return self._parser[GENERAL_SETTINGS_SECTION_NAME]["font_name"]

    @font_name.setter
    def font_name(self, value):
        self._parser[GENERAL_SETTINGS_SECTION_NAME]["font_name"] = str(value)

    @property
    def font_size(self):
        return self._parser[GENERAL_SETTINGS_SECTION_NAME]["font_size"]

    @font_size.setter
    def font_size(self, value):
        self._parser[GENERAL_SETTINGS_SECTION_NAME]["font_size"] = str(value)

    @property
    def background_color(self):
        return self._parser[GENERAL_SETTINGS_SECTION_NAME]["background_color"]

    @background_color.setter
    def background_color(self, value):
        self._parser[GENERAL_SETTINGS_SECTION_NAME]["background_color"] = str(value)

    @property
    def foreground_color(self):
        return self._parser[GENERAL_SETTINGS_SECTION_NAME]["foreground_color"]

    @foreground_color.setter
    def foreground_color(self, value):
        self._parser[GENERAL_SETTINGS_SECTION_NAME]["foreground_color"] = str(value)

    def dump(self):
        with open(file=SETTINGS_FILE_PATH, mode="w") as configfile:
            self._parser.write(configfile)
