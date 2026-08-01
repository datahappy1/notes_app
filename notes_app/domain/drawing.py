import json
from dataclasses import dataclass, asdict


@dataclass
class Stroke:
    tool: str
    points: list


class Drawing:
    def __init__(self):
        self.strokes = []

    def add_stroke(self, tool, points):
        self.strokes.append(
            Stroke(
                tool=tool,
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
                drawing.strokes.append(
                    Stroke(**stroke)
                )

        except FileNotFoundError:
            pass

        return drawing
