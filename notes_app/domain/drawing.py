import os
import json
from dataclasses import dataclass, asdict, field


@dataclass
class Stroke:
    tool: str
    points: list
    color: tuple = field(default_factory=lambda: (0, 0, 0, 1))


class Drawing:
    def __init__(self):
        self.strokes = []

    def add_stroke(self, tool, current_color, points):
        self.strokes.append(
            Stroke(
                tool=tool,
                color=current_color,
                points=points,
            )
        )

    def save(self, filename):
        with open(filename, "w", encoding="utf8") as f:
            json.dump(
                [asdict(x) for x in self.strokes],
                f,
                indent=4,
            )

    @classmethod
    def load(cls, filename):
        drawing = cls()

        try:
            with open(filename, encoding="utf8") as f:
                data = json.load(f)
            for stroke in data:
                if "color" not in stroke:
                    stroke["color"] = (0, 0, 0, 1)

                drawing.strokes.append(Stroke(**stroke))

        except FileNotFoundError:
            pass

        return drawing

    @staticmethod
    def rename_files(old_json_path, new_json_path, old_png_path, new_png_path):
        try:
            os.rename(old_json_path, new_json_path)
            os.rename(old_png_path, new_png_path)
        except FileNotFoundError as file_not_found:
            raise file_not_found
        except Exception as exc:
            raise exc

    @staticmethod
    def delete_files(json_path, png_path):
        try:
            os.remove(json_path)
            os.remove(png_path)
        except FileNotFoundError as file_not_found:
            raise file_not_found
        except Exception as exc:
            raise exc
