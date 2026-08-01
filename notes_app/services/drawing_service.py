import re
from pathlib import Path

from notes_app.domain.drawing import Drawing


class DrawingService:
    def __init__(self, working_directory="."):
        self.working_directory = Path(working_directory)

    def _safe_name(self, section):
        return re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            section,
        )

    def json_path(self, section):
        return self.working_directory / (
            self._safe_name(section) + ".json"
        )

    def png_path(self, section):
        return self.working_directory / (
            self._safe_name(section) + ".png"
        )

    def load(self, section):
        return Drawing.load(
            self.json_path(section)
        )

    def save(self, section, drawing):
        drawing.save(
            self.json_path(section)
        )
