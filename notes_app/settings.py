class Settings:
    def __init__(self, store, defaults):
        self.defaults = defaults
        self.store = store(filename=self.defaults.DEFAULT_SETTINGS_STORE_FILE_NAME)
        self._set_missing_store_defaults()

        self._font_name = self.store.get("font_name")["value"]
        self._font_size = self.store.get("font_size")["value"]
        self._background_color = self.store.get("background_color")["value"]
        self._foreground_color = self.store.get("foreground_color")["value"]

    def _set_missing_store_defaults(self):
        if (
            not self.store.exists("font_name")
            or self.store.get("font_name")["value"] is None
        ):
            self.store.put(
                "font_name", value=self.defaults.DEFAULT_SETTINGS_VALUE_FONT_NAME
            )

        if (
            not self.store.exists("font_size")
            or self.store.get("font_size")["value"] is None
        ):
            self.store.put(
                "font_size", value=self.defaults.DEFAULT_SETTINGS_VALUE_FONT_SIZE
            )

        if (
            not self.store.exists("background_color")
            or self.store.get("background_color")["value"] is None
        ):
            self.store.put(
                "background_color",
                value=self.defaults.DEFAULT_SETTINGS_VALUE_BACKGROUND_COLOR,
            )

        if (
            not self.store.exists("foreground_color")
            or self.store.get("foreground_color")["value"] is None
        ):
            self.store.put(
                "foreground_color",
                value=self.defaults.DEFAULT_SETTINGS_VALUE_FOREGROUND_COLOR,
            )

    @property
    def font_name(self):
        return self._font_name

    @font_name.setter
    def font_name(self, value):
        self._font_name = str(value)

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = str(value)

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value):
        self._background_color = str(value)

    @property
    def foreground_color(self):
        return self._foreground_color

    @foreground_color.setter
    def foreground_color(self, value):
        self._foreground_color = str(value)

    def dump(self):
        self.store.put("font_name", value=self._font_name)
        self.store.put("font_size", value=self._font_size)
        self.store.put("background_color", value=self._background_color)
        self.store.put("foreground_color", value=self._foreground_color)
