from configparser import ConfigParser
from os import getcwd


class StaticSettings:
    APP_STARTUP_FILE_PATH = f"{getcwd()}/assets/sample.txt"
    APP_SETTINGS_FILE_PATH = f"{getcwd()}/settings.conf"


class Settings:
    def __init__(self):
        self._parser = ConfigParser()
        self._parser.read(StaticSettings.APP_SETTINGS_FILE_PATH)

        self.parsed = dict()
        for name, value in self._parser.items("general_settings"):
            if value in ("True", "true"):
                self.parsed[name] = True
            elif value in ("False", "false"):
                self.parsed[name] = False
            else:
                self.parsed[name] = value

    @property
    def font_size(self):
        return self.parsed["font_size"]

    @font_size.setter
    def font_size(self, value):
        self.parsed["font_size"] = value

    def _transform_settings_to_lines(self):
        lines = []
        for item in self.parsed.items():
            lines.append(f"{item[0]} = {item[1]}")
        return lines

    def dump(self):
        with open(file=StaticSettings.APP_SETTINGS_FILE_PATH, mode="w") as f:
            f.write("[general_settings]\n")
            f.writelines(self._transform_settings_to_lines())
