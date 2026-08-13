import re
from pathlib import Path

from notes_app.domain.drawing import Drawing


class DrawingService:
    def __init__(self, defaults):
        self.defaults = defaults

    def _safe_name(self, section):
        return re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            section,
        )

    def json_path(self, section):
        return Path(self.defaults.BASE_FILE_PATH) / f"{self._safe_name(section)}.json"

    def png_path(self, section):
        return Path(self.defaults.BASE_FILE_PATH) / f"{self._safe_name(section)}.png"

    def load(self, section):
        return Drawing.load(self.json_path(section))

    def save(self, section, drawing):
        drawing.save(self.json_path(section))

    @staticmethod
    def _is_drawing_in_section(json_drawing_file_path, png_drawing_file_path):
        print(json_drawing_file_path, png_drawing_file_path)
        return (
            Path(json_drawing_file_path).is_file()
            and Path(png_drawing_file_path).is_file()
        )

    def rename_section(self, old_section, new_section):
        old_section_json_path = self.json_path(self._safe_name(old_section))
        old_section_png_path = self.png_path(self._safe_name(old_section))

        if self._is_drawing_in_section(old_section_json_path, old_section_png_path):
            new_section_json_path = self.json_path(self._safe_name(new_section))
            new_section_png_path = self.png_path(self._safe_name(new_section))

            Drawing.rename_files(
                old_section_json_path,
                new_section_json_path,
                old_section_png_path,
                new_section_png_path,
            )

    def delete_section(self, section):
        section_json_path = self.json_path(self._safe_name(section))
        section_png_path = self.png_path(self._safe_name(section))

        if self._is_drawing_in_section(section_json_path, section_png_path):
            Drawing.delete_files(section_json_path, section_png_path)
