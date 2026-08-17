from notes_app.domain.drawing import Drawing, Stroke
from notes_app.services.drawing_service import DrawingService


class TestDrawingService:
    def test_load(self, get_defaults, get_test_section_name, get_notes_file):
        service = DrawingService(
            defaults=get_defaults,
            file=get_notes_file,
        )

        section_separator = get_defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(
            name=get_test_section_name
        )

        get_notes_file.set_section_content(
            section_separator,
            "",
        )

        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        drawing_text = Drawing.replace_in_text(
            get_notes_file.get_section_content(section_separator),
            drawing,
        )

        get_notes_file.set_section_content(
            section_separator,
            drawing_text,
        )

        loaded = service.load(get_test_section_name)

        assert loaded.strokes == [
            Stroke(
                tool="pen",
                points=[[1, 2]],
                color=(1, 0, 0, 1),
            )
        ]

    def test_save(self, get_defaults, get_test_section_name, get_notes_file):
        service = DrawingService(
            defaults=get_defaults,
            file=get_notes_file,
        )

        section_separator = get_defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(
            name=get_test_section_name
        )

        get_notes_file.set_section_content(
            section_separator,
            "",
        )

        drawing = Drawing()
        drawing.add_stroke(
            "pen",
            (1, 0, 0, 1),
            [(1, 2)],
        )

        service.save(
            get_test_section_name,
            drawing,
        )

        loaded = service.load(get_test_section_name)

        assert loaded.strokes == [
            Stroke(
                tool="pen",
                points=[[1, 2]],
                color=(1, 0, 0, 1),
            )
        ]
