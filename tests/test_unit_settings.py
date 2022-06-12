class TestSettings:
    def test__set_missing_store_defaults(self, get_settings):
        get_settings.store.font_name = None
        get_settings.store.font_size = None
        get_settings.store.background_color = None
        get_settings.store.foreground_color = None

        get_settings._set_missing_store_defaults()

        assert get_settings.store["font_name"] == {"value": "Roboto-Bold"}
        assert get_settings.store["font_size"] == {"value": "14.0"}
        assert get_settings.store["background_color"] == {"value": "blue"}
        assert get_settings.store["foreground_color"] == {"value": "green"}

    def test_set_get_font_name(self, get_settings):
        get_settings.font_name = "Roboto"
        assert get_settings.font_name == "Roboto"

    def test_set_get_font_size(self, get_settings):
        get_settings.font_size = "20"
        assert get_settings.font_size == "20"

    def test_set_get_background_color(self, get_settings):
        get_settings.background_color = "red"
        assert get_settings.background_color == "red"

    def test_set_get_foreground_color(self, get_settings):
        get_settings.foreground_color = "yellow"
        assert get_settings.foreground_color == "yellow"

    def test_dump(self, get_settings):
        get_settings.font_name = "arial"
        get_settings.font_size = "50.0"
        get_settings.background_color = "blue"
        get_settings.foreground_color = "olive"
        assert get_settings.dump() is None

        assert get_settings.store["font_name"] == {"value": "arial"}
        assert get_settings.store["font_size"] == {"value": "50.0"}
        assert get_settings.store["background_color"] == {"value": "blue"}
        assert get_settings.store["foreground_color"] == {"value": "olive"}
