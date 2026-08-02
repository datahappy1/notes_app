from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from kivy.uix.widget import Widget


class DrawingCanvas(Widget):
    def __init__(self, drawing, **kwargs):
        super().__init__(**kwargs)

        self.drawing = drawing

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.background = Rectangle(
                pos=self.pos,
                size=self.size,
            )

        self.drawing_layer = InstructionGroup()
        self.canvas.add(self.drawing_layer)

        self.bind(
            pos=self._update_background,
            size=self._update_background,
        )

        self.current_color = (0, 0, 0, 1)
        self.current_stroke = []
        self.current_line = None

        self.bind(size=lambda *_: self.redraw())
        self.bind(pos=lambda *_: self.redraw())

        self.redraw()
        self.tool = "pencil"

    def set_color(self, color):
        self.current_color = color

    def clear(self):
        self.drawing.strokes.clear()
        self.redraw()

    def undo(self):
        if len(self.drawing.strokes) > 1:
            self.drawing.strokes.pop()
            self.drawing.strokes.pop()
            self.redraw()

    def redraw(self):
        self.drawing_layer.clear()

        for stroke in self.drawing.strokes:
            self.drawing_layer.add(
                Color(*stroke.color)
            )

            self.drawing_layer.add(
                Line(
                    points=stroke.points,
                    width=2,
                )
            )

    def _update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size

    def _pencil_down(self, touch):
        self.current_stroke = [touch.x, touch.y]
        self.drawing_layer.add(
            Color(*self.current_color)
        )
        self.current_line = Line(
            points=self.current_stroke,
            width=2,
        )

        self.drawing_layer.add(self.current_line)
        return True

    def _pencil_move(self, touch):
        self.current_stroke.extend([touch.x, touch.y])
        self.current_line.points = self.current_stroke

        return True

    def _pencil_up(self, touch):
        self.drawing.add_stroke(
            tool=self.tool,
            current_color=self.current_color,
            points=self.current_stroke.copy(),
        )
        self.redraw()
        return True

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        return self._pencil_down(touch)

    def on_touch_move(self, touch):
        return self._pencil_move(touch)

    def on_touch_up(self, touch):
        return self._pencil_up(touch)
