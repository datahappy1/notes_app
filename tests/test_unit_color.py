from notes_app.color import (
    Color,
    get_color_by_name,
    AVAILABLE_COLORS,
    get_next_color_by_rgba,
)


class TestColor:
    def test_color(self):
        assert Color("black", (0, 0, 0, 1))
        assert Color("white", (1, 1, 1, 1))

    def test_get_color_by_name(self):
        assert (
            get_color_by_name(colors_list=AVAILABLE_COLORS, color_name="black").name
            == "black"
        )
        assert get_color_by_name(
            colors_list=AVAILABLE_COLORS, color_name="black"
        ).rgba_value == (0, 0, 0, 1)
        assert (
            get_color_by_name(colors_list=AVAILABLE_COLORS, color_name="white").name
            == "white"
        )
        assert get_color_by_name(
            colors_list=AVAILABLE_COLORS, color_name="white"
        ).rgba_value == (1, 1, 1, 1)

    def test_get_last_color(self):
        assert (
            get_next_color_by_rgba(
                colors_list=AVAILABLE_COLORS, rgba_value=[1, 1, 1, 1]
            ).name
            == "black"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS, rgba_value=[1, 1, 1, 1]
        ).rgba_value == (0, 0, 0, 1)

        assert (
            get_next_color_by_rgba(
                colors_list=AVAILABLE_COLORS,
                rgba_value=[1, 1, 1, 1],
                skip_rgba_value=[1, 1, 1, 1],
            ).name
            == "black"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS,
            rgba_value=[1, 1, 1, 1],
            skip_rgba_value=[1, 1, 1, 1],
        ).rgba_value == (0, 0, 0, 1)

        assert (
            get_next_color_by_rgba(
                colors_list=AVAILABLE_COLORS,
                rgba_value=[1, 1, 1, 1],
                skip_rgba_value=[0, 0, 0, 1],
            ).name
            == "navy"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS,
            rgba_value=[1, 1, 1, 1],
            skip_rgba_value=[0, 0, 0, 1],
        ).rgba_value == (0, 0, 0.5, 1)

        assert (
            get_next_color_by_rgba(
                colors_list=AVAILABLE_COLORS,
                rgba_value=[1, 1, 0, 1],
                skip_rgba_value=[1, 1, 1, 1],
            ).name
            == "black"
        )
        assert get_next_color_by_rgba(
            colors_list=AVAILABLE_COLORS,
            rgba_value=[1, 1, 0, 1],
            skip_rgba_value=[1, 1, 1, 1],
        ).rgba_value == (0, 0, 0, 1)
