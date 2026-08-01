from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget


class DrawingCanvas(Widget):
    def __init__(self, drawing, **kwargs):
        super().__init__(**kwargs)

        self.drawing = drawing

        with self.canvas.before:
            Color(1, 1, 1, 1)  # white
            self.background = Rectangle(
                pos=self.pos,
                size=self.size,
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background,
        )

        self.current_points = []
        self.current_line = None

        self.bind(size=lambda *_: self.redraw())
        self.bind(pos=lambda *_: self.redraw())

        self.redraw()
        self.tool = "pencil"

    def redraw(self):
        self.canvas.clear()

        with self.canvas:
            Color(0, 0, 0)

            for stroke in self.drawing.strokes:
                Line(points=stroke.points, width=2)

    def _update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size

    def _pencil_down(self, touch):
        self.current_points = [touch.x, touch.y]
        with self.canvas:
            Color(0, 0, 0)
            self.current_line = Line(
                points=self.current_points,
                width=2,
            )

        return True

    def _pencil_move(self, touch):
        self.current_points.extend([touch.x, touch.y])
        self.current_line.points = self.current_points

        return True

    def _pencil_up(self, touch):
        self.drawing.add_stroke(
            self.tool,
            self.current_points,
        )

        return True

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        return self._pencil_down(touch)

    def on_touch_move(self, touch):
        return self._pencil_move(touch)

    def on_touch_up(self, touch):
        return self._pencil_up(touch)
