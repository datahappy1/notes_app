DEFAULT_SETTINGS_STORE_FILE_NAME = "settings.json"

DEFAULT_SETTINGS_VALUE_FONT_NAME = "RobotoMono-Regular"
DEFAULT_SETTINGS_VALUE_FONT_SIZE = "14.0"
DEFAULT_SETTINGS_VALUE_BACKGROUND_COLOR = "black"
DEFAULT_SETTINGS_VALUE_FOREGROUND_COLOR = "green"


class Settings:
    def __init__(self, store):
        self.store = store(filename=DEFAULT_SETTINGS_STORE_FILE_NAME)
        self._set_store_default_value_if_empty()

    def _set_store_default_value_if_empty(self):
        if not self.store.exists('font_name') or self.store.get("font_name")["value"] is None:
            self.store.put("font_name", value=DEFAULT_SETTINGS_VALUE_FONT_NAME)

        if not self.store.exists('font_size') or self.store.get("font_size")["value"] is None:
            self.store.put("font_size", value=DEFAULT_SETTINGS_VALUE_FONT_SIZE)

        if not self.store.exists('background_color') or self.store.get("background_color")["value"] is None:
            self.store.put("background_color", value=DEFAULT_SETTINGS_VALUE_BACKGROUND_COLOR)

        if not self.store.exists('foreground_color') or self.store.get("foreground_color")["value"] is None:
            self.store.put("foreground_color", value=DEFAULT_SETTINGS_VALUE_FOREGROUND_COLOR)

    @property
    def font_name(self):
        return self.store.get("font_name")["value"]

    @font_name.setter
    def font_name(self, value):
        self.store.put("font_name", value=str(value))

    @property
    def font_size(self):
        return self.store.get("font_size")["value"]

    @font_size.setter
    def font_size(self, value):
        self.store.put("font_size", value=str(value))

    @property
    def background_color(self):
        return self.store.get("background_color")["value"]

    @background_color.setter
    def background_color(self, value):
        self.store.put("background_color", value=str(value))

    @property
    def foreground_color(self):
        return self.store.get("foreground_color")["value"]

    @foreground_color.setter
    def foreground_color(self, value):
        self.store.put("foreground_color", value=str(value))
