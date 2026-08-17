import json
from dataclasses import dataclass, asdict, field


@dataclass
class Stroke:
    tool: str
    points: list
    color: tuple = field(default_factory=lambda: (0, 0, 0, 1))


class Drawing:
    DRAWING_START = "<drawing>"
    DRAWING_END = "</drawing>"
    DRAWING_VERSION = 1

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

    def to_dict(self):
        return {
            "version": self.DRAWING_VERSION,
            "strokes": [asdict(stroke) for stroke in self.strokes],
        }

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            indent=4,
        )

    @classmethod
    def from_dict(cls, data):
        drawing = cls()

        if not isinstance(data, dict):
            return drawing

        if data.get("version") != cls.DRAWING_VERSION:
            return drawing

        for stroke in data.get("strokes", []):
            if "color" not in stroke:
                stroke["color"] = (0, 0, 0, 1)
            else:
                stroke["color"] = tuple(stroke["color"])

            drawing.strokes.append(Stroke(**stroke))

        return drawing

    @classmethod
    def from_json(cls, value):
        try:
            data = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return cls()

        return cls.from_dict(data)

    def to_text(self):
        return f"{self.DRAWING_START}\n" f"{self.to_json()}\n" f"{self.DRAWING_END}"

    @classmethod
    def from_text(cls, text):
        start = text.find(cls.DRAWING_START)
        end = text.find(cls.DRAWING_END)

        if start == -1 or end == -1 or end < start:
            return cls()

        start += len(cls.DRAWING_START)
        json_text = text[start:end].strip()

        return cls.from_json(json_text)

    @classmethod
    def remove_from_text(cls, text):
        start = text.find(cls.DRAWING_START)
        end = text.find(cls.DRAWING_END)

        if start == -1 or end == -1 or end < start:
            return text

        end += len(cls.DRAWING_END)

        if end < len(text) and text[end] == "\n":
            end += 1
        elif start > 0 and text[start - 1] == "\n":
            start -= 1

        return text[:start] + text[end:]

    @classmethod
    def replace_in_text(cls, text, drawing):
        clean_text = cls.remove_from_text(text).rstrip()

        if not drawing.strokes:
            return clean_text

        if clean_text:
            return f"{clean_text}\n\n{drawing.to_text()}"

        return drawing.to_text()
