from pathlib import Path

from kivymd.uix.boxlayout import MDBoxLayout

from notes_app.domain.drawing import Drawing, Stroke
from notes_app.services.drawing_service import DrawingService
from notes_app.view.drawing_window import DrawingWindow


class TestDrawingWindow:

    def test_init(self, get_defaults):
        service = DrawingService(defaults=get_defaults)
        drawing = Drawing()
        drawing.save("Test.json")

        window = DrawingWindow("Test", service)

        assert window.section == "Test"
        assert window.service is service
        assert window.drawing.strokes == drawing.strokes
        assert window.canvas_widget.drawing is window.drawing

    def test_create_separator(self, get_defaults):
        window = DrawingWindow("Test", DrawingService(defaults=get_defaults))

        separator = window.create_separator()

        assert isinstance(separator, MDBoxLayout)

    def test_get_colored_pen_button(self, get_defaults):
        window = DrawingWindow("Test", DrawingService(defaults=get_defaults))
        color = (1, 0, 0, 1)
        button = window.get_colored_pen_button(color)
        assert button.icon == "pencil-circle-outline"
        assert button.icon_color == list(color)

    def test_select_icon(self, get_defaults):
        window = DrawingWindow("Test", DrawingService(defaults=get_defaults))
        button = window.color_buttons[1]

        window.select_icon(button, (1, 0, 0, 1))

        assert window.canvas_widget.current_color == (1, 0, 0, 1)
        assert button.icon == "pencil-circle"
        assert all(
            color_button.icon == "pencil-circle-outline"
            for color_button in window.color_buttons
            if color_button is not button
        )

    def test_save(self, get_defaults):
        service = DrawingService(defaults=get_defaults)
        window = DrawingWindow("Test", service)
        window.drawing.add_stroke(
            "pencil",
            (1, 0, 0, 1),
            [10, 20, 30, 40],
        )
        window.save()
        loaded = Drawing.load("Test.json")

        assert loaded.strokes == [
            Stroke(
                tool="pencil",
                points=[10, 20, 30, 40],
                color=[1, 0, 0, 1],
            )
        ]
