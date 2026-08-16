from kivymd.uix.boxlayout import MDBoxLayout

from notes_app.domain.drawing import Stroke


class TestDrawingWindow:
    def test_init(self, get_drawing_window, get_defaults, get_notes_file):
        assert get_drawing_window.section == "Test"
        assert get_drawing_window.service.file is get_notes_file
        assert get_drawing_window.drawing.strokes == []
        assert get_drawing_window.canvas_widget.drawing is get_drawing_window.drawing

    def test_create_separator(self, get_drawing_window, get_defaults, get_notes_file):
        separator = get_drawing_window.create_separator()

        assert isinstance(separator, MDBoxLayout)

    def test_get_colored_pen_button(
        self, get_drawing_window, get_defaults, get_notes_file
    ):
        color = (1, 0, 0, 1)
        button = get_drawing_window.get_colored_pen_button(color)

        assert button.icon == "pencil-circle-outline"
        assert button.icon_color == list(color)

    def test_select_icon(self, get_drawing_window, get_defaults, get_notes_file):
        button = get_drawing_window.color_buttons[1]

        get_drawing_window.select_icon(button, (1, 0, 0, 1))

        assert get_drawing_window.canvas_widget.current_color == (1, 0, 0, 1)
        assert button.icon == "pencil-circle"

        assert all(
            color_button.icon == "pencil-circle-outline"
            for color_button in get_drawing_window.color_buttons
            if color_button is not button
        )

    def test_save(self, get_drawing_window, get_defaults, get_notes_file):
        get_drawing_window.drawing.add_stroke(
            "pencil",
            (1, 0, 0, 1),
            [10, 20, 30, 40],
        )

        get_drawing_window.save()

        loaded = get_drawing_window.service.load("Test")

        assert loaded.strokes == [
            Stroke(
                tool="pencil",
                points=[10, 20, 30, 40],
                color=(1, 0, 0, 1),
            )
        ]
