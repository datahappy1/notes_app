from pathlib import Path

from notes_app.domain.drawing import Drawing, Stroke
from notes_app.services.drawing_service import DrawingService


class TestDrawingService:
    def test_safe_name(self, get_defaults):
        service = DrawingService(defaults=get_defaults)
        assert service._safe_name("My Section: Test!") == "My_Section__Test_"

    def test_json_path(self, get_defaults):
        service = DrawingService(defaults=get_defaults)
        assert service.json_path("My Section") == Path("My_Section.json")

    def test_png_path(self, get_defaults):
        service = DrawingService(defaults=get_defaults)
        assert service.png_path("My Section") == Path("My_Section.png")

    def test_load(self, get_defaults, get_test_section_name):
        service = DrawingService(defaults=get_defaults)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        drawing.save(f"{get_test_section_name}.json")

        loaded = service.load(get_test_section_name)

        assert loaded.strokes == [
            Stroke(
                tool="pen",
                points=[[1, 2]],
                color=[1, 0, 0, 1],
            )
        ]

    def test_save(self, get_defaults, get_test_section_name):
        service = DrawingService(defaults=get_defaults)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        service.save(get_test_section_name, drawing)

        loaded = Drawing.load(f"{get_test_section_name}.json")

        assert loaded.strokes == [
            Stroke(
                tool="pen",
                points=[[1, 2]],
                color=[1, 0, 0, 1],
            )
        ]

    def test_is_drawing_in_section(self, get_app, get_defaults, get_test_section_name):
        service = DrawingService(defaults=get_defaults)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        service.save(get_test_section_name, drawing)
        get_app.controller.get_screen().export_to_png(f"{get_test_section_name}.png")

        assert (
            service._is_drawing_in_section(
                png_drawing_file_path=f"{get_test_section_name}.png",
                json_drawing_file_path=f"{get_test_section_name}.json",
            )
            is True
        )

    def test_rename_section(self, get_app, get_defaults, get_test_section_name):
        service = DrawingService(defaults=get_defaults)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )
        drawing.save(f"first.json")
        get_app.controller.get_screen().export_to_png(f"first.png")

        service.rename_section("first", f"{get_test_section_name}")

        assert service._is_drawing_in_section(
            json_drawing_file_path=f"{get_test_section_name}.json",
            png_drawing_file_path=f"{get_test_section_name}.png",
        )
        assert drawing.load(f"{get_test_section_name}.json").strokes == [
            Stroke(tool="pen", points=[[1, 2]], color=[1, 0, 0, 1])
        ]

    def test_delete_section(self, get_app, get_defaults):
        service = DrawingService(defaults=get_defaults)
        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )
        drawing.save(f"first.json")
        get_app.controller.get_screen().export_to_png(f"first.png")

        assert service._is_drawing_in_section(
            json_drawing_file_path="first.json", png_drawing_file_path="first.png"
        )

        service.delete_section("first")

        assert (
            service._is_drawing_in_section(
                json_drawing_file_path="first.json", png_drawing_file_path="first.png"
            )
            is False
        )
