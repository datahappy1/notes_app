from notes_app.font import get_next_font, AVAILABLE_FONTS


class TestFont:
    def test_get_last_font(self):
        assert (
            get_next_font(fonts_list=AVAILABLE_FONTS, font_name="RobotoMono-Regular")
            == "DejaVuSans"
        )
