from notes_app.domain.drawing import Drawing


class DrawingService:
    def __init__(self, file, defaults):
        self.file = file
        self.defaults = defaults

    def load(self, section):
        drawing = Drawing.from_text(
            self.file.get_section_content(
                self.defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(name=section)
            )
        )

        if drawing is None:
            return Drawing()

        return drawing

    def save(self, section, drawing):
        section_separator = self.defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(
            name=section
        )

        current_text = self.file.get_section_content(section_separator)

        new_text = Drawing.replace_in_text(
            current_text,
            drawing,
        )

        self.file.set_section_content(
            section_separator=section_separator,
            section_content=new_text,
        )

        self.file.save_file_data()
