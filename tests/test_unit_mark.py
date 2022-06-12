from notes_app.mark import get_marked_text


class TestMark:
    def test_get_marked_search_result(self):
        assert (
            get_marked_text(
                text="some string",
                highlight_style="some_style",
                highlight_color="some_color",
            )
            == "[some_style][color=some_color]some string[/color][/some_style]"
        )
