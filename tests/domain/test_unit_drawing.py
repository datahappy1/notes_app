import json

from notes_app.domain.drawing import Drawing, Stroke


class TestStroke:
    def test_default_color(self):
        stroke = Stroke("pen", [(1, 2)])

        assert stroke.tool == "pen"
        assert stroke.points == [(1, 2)]
        assert stroke.color == (0, 0, 0, 1)


class TestDrawing:
    def test_init(self):
        drawing = Drawing()

        assert drawing.strokes == []

    def test_add_stroke(self):
        drawing = Drawing()
        points = [(1, 2), (3, 4)]
        color = (1, 0, 0, 1)

        drawing.add_stroke("pen", color, points)

        assert drawing.strokes == [Stroke("pen", points, color)]

    def test_remove_from_text(self):
        text = "notes\n<drawing>old drawing</drawing>\nmore notes"

        result = Drawing.remove_from_text(text)

        assert result == "notes\nmore notes"

    def test_replace_in_text(self):
        text = "notes\n<drawing>old drawing</drawing>\nmore notes"

        drawing = Drawing()
        drawing.add_stroke(
            tool="pencil",
            current_color=(1, 0, 0, 1),
            points=[1, 2, 3, 4],
        )

        result = Drawing.replace_in_text(text, drawing)
        assert result == (
            "notes\n"
            "more notes\n"
            "\n"
            "<drawing>\n"
            "{\n"
            '    "version": 1,\n'
            '    "strokes": [\n'
            "        {\n"
            '            "tool": "pencil",\n'
            '            "points": [\n'
            "                1,\n"
            "                2,\n"
            "                3,\n"
            "                4\n"
            "            ],\n"
            '            "color": [\n'
            "                1,\n"
            "                0,\n"
            "                0,\n"
            "                1\n"
            "            ]\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "</drawing>"
        )
