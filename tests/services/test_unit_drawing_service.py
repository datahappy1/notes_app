from pathlib import Path

from notes_app.domain.drawing import Drawing, Stroke
from notes_app.services.drawing_service import DrawingService


class TestDrawingService:
    def test_init(self):
        service = DrawingService("drawings")
        assert service.working_directory == Path("drawings")

    def test_safe_name(self):
        service = DrawingService()
        assert service._safe_name("My Section: Test!") == "My_Section__Test_"

    def test_json_path(self):
        service = DrawingService("drawings")
        assert service.json_path("My Section") == Path(
            "drawings/My_Section.json"
        )

    def test_png_path(self):
        service = DrawingService("drawings")
        assert service.png_path("My Section") == Path(
            "drawings/My_Section.png"
        )

    def test_load(self, tmp_path):
        service = DrawingService(tmp_path)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        drawing.save(tmp_path / "My_Section.json")

        loaded = service.load("My Section")

        assert loaded.strokes == [
            Stroke(
                tool="pen",
                points=[[1, 2]],
                color=[1, 0, 0, 1],
            )
        ]

    def test_save(self, tmp_path):
        service = DrawingService(tmp_path)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        service.save("My Section", drawing)

        loaded = Drawing.load(tmp_path / "My_Section.json")

        assert loaded.strokes == [
            Stroke(
                tool="pen",
                points=[[1, 2]],
                color=[1, 0, 0, 1],
            )
        ]

