from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from kivy.uix.widget import Widget
from notes_app.domain.drawing import Drawing


class DrawingCanvas(Widget):
    LINE_WIDTH = 2

    def __init__(self, drawing, **kwargs):
        super().__init__(**kwargs)

        self.drawing = drawing if drawing is not None else Drawing()

        self.current_color = (0, 0, 0, 1)
        self.current_stroke_color = self.current_color

        self.current_stroke = []
        self.current_line = None
        self.active_touch = None
        self.tool = "pencil"

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

        self.bind(
            size=lambda *_: self.redraw(),
            pos=lambda *_: self.redraw(),
        )

        self.redraw()

    def set_color(self, color):
        self.current_color = tuple(color)

    def clear(self):
        """Remove all strokes and reset the active stroke state."""
        self._reset_current_stroke()

        self.drawing.strokes.clear()
        self.redraw()

    def undo(self):
        """Remove the most recently completed stroke."""
        self._reset_current_stroke()

        if not self.drawing.strokes:
            return

        self.drawing.strokes.pop()
        self.redraw()

    def redraw(self):
        """Rebuild the visible drawing from the stored strokes."""
        self.drawing_layer.clear()

        for stroke in self.drawing.strokes:
            if len(stroke.points) < 4:
                continue

            self.drawing_layer.add(Color(*stroke.color))

            self.drawing_layer.add(
                Line(
                    points=stroke.points,
                    width=self.LINE_WIDTH,
                )
            )

    def _update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size

    def _pencil_down(self, touch):
        # Do not start another stroke while one is active.
        if self.active_touch is not None:
            return False

        self.active_touch = touch
        self.current_stroke = [touch.x, touch.y]
        self.current_stroke_color = tuple(self.current_color)

        self.drawing_layer.add(Color(*self.current_stroke_color))

        self.current_line = Line(
            points=self.current_stroke,
            width=self.LINE_WIDTH,
        )

        self.drawing_layer.add(self.current_line)

        return True

    def _pencil_move(self, touch):
        if touch is not self.active_touch:
            return False

        if self.current_line is None:
            return False

        self.current_stroke.extend([touch.x, touch.y])
        self.current_line.points = self.current_stroke

        return True

    def _pencil_up(self, touch):
        if touch is not self.active_touch:
            return False

        try:
            # Ignore taps / incomplete strokes.
            if len(self.current_stroke) >= 4:
                self.drawing.add_stroke(
                    tool=self.tool,
                    current_color=self.current_stroke_color,
                    points=self.current_stroke.copy(),
                )

            # Rebuild graphics from the model.
            self.redraw()

            return True

        finally:
            self._reset_current_stroke()

    def _reset_current_stroke(self):
        self.active_touch = None
        self.current_stroke = []
        self.current_line = None
        self.current_stroke_color = tuple(self.current_color)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        return self._pencil_down(touch)

    def on_touch_move(self, touch):
        return self._pencil_move(touch)

    def on_touch_up(self, touch):
        return self._pencil_up(touch)
