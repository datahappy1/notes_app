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

    def test_save(self, tmp_path):
        drawing = Drawing()
        drawing.add_stroke("pen", (1, 0, 0, 1), [(1, 2)])

        filename = tmp_path / "drawing.json"
        drawing.save(filename)

        data = json.loads(filename.read_text())

        assert data == [
            {
                "tool": "pen",
                "points": [[1, 2]],
                "color": [1, 0, 0, 1],
            }
        ]

    def test_load(self, tmp_path):
        filename = tmp_path / "drawing.json"
        filename.write_text(
            json.dumps(
                [
                    {
                        "tool": "pen",
                        "points": [[1, 2]],
                        "color": [1, 0, 0, 1],
                    }
                ]
            )
        )

        drawing = Drawing.load(filename)

        assert drawing.strokes == [Stroke("pen", [[1, 2]], [1, 0, 0, 1])]

    def test_load_without_color(self, tmp_path):
        filename = tmp_path / "drawing.json"
        filename.write_text(
            json.dumps(
                [
                    {
                        "tool": "pen",
                        "points": [[1, 2]],
                    }
                ]
            )
        )

        drawing = Drawing.load(filename)

        assert drawing.strokes == [Stroke("pen", [[1, 2]], (0, 0, 0, 1))]
