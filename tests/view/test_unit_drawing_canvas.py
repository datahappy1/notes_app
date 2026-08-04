from types import SimpleNamespace

from notes_app.domain.drawing import Drawing, Stroke
from notes_app.view.drawing_canvas import DrawingCanvas


class TestDrawingCanvas:
    @staticmethod
    def touch(x=10, y=20):
        return SimpleNamespace(x=x, y=y, pos=(x, y))

    def test_init(self):
        drawing = Drawing()

        canvas = DrawingCanvas(drawing)

        assert canvas.drawing is drawing
        assert canvas.current_color == (0, 0, 0, 1)
        assert canvas.tool == "pencil"
        assert canvas.current_stroke == []
        assert canvas.active_touch is None

    def test_set_color(self):
        canvas = DrawingCanvas(Drawing())

        canvas.set_color([1, 0, 0, 1])

        assert canvas.current_color == (1, 0, 0, 1)

    def test_clear(self):
        drawing = Drawing()
        drawing.add_stroke("pencil", (1, 0, 0, 1), [1, 2, 3, 4])
        canvas = DrawingCanvas(drawing)

        canvas.clear()

        assert drawing.strokes == []
        assert canvas.current_stroke == []
        assert canvas.active_touch is None
        assert canvas.current_line is None

    def test_undo(self):
        drawing = Drawing()
        drawing.add_stroke("pencil", (1, 0, 0, 1), [1, 2, 3, 4])
        drawing.add_stroke("pencil", (0, 1, 0, 1), [5, 6, 7, 8])
        canvas = DrawingCanvas(drawing)

        canvas.undo()

        assert len(drawing.strokes) == 1
        assert drawing.strokes[0].points == [1, 2, 3, 4]

    def test_redraw(self):
        drawing = Drawing()
        drawing.add_stroke(
            "pencil",
            (1, 0, 0, 1),
            [1, 2, 3, 4],
        )
        canvas = DrawingCanvas(drawing)

        canvas.redraw()

        assert drawing.strokes == [
            Stroke(
                "pencil",
                [1, 2, 3, 4],
                (1, 0, 0, 1),
            )
        ]

    def test_update_background(self):
        canvas = DrawingCanvas(Drawing())
        canvas.pos = (10, 20)
        canvas.size = (300, 400)

        canvas._update_background()

        assert tuple(canvas.background.pos) == tuple(canvas.pos)
        assert tuple(canvas.background.size) == tuple(canvas.size)

    def test_pencil_down(self):
        canvas = DrawingCanvas(Drawing())
        touch = self.touch()

        result = canvas._pencil_down(touch)

        assert result is True
        assert canvas.active_touch is touch
        assert canvas.current_stroke == [10, 20]
        assert canvas.current_line is not None

    def test_pencil_move(self):
        canvas = DrawingCanvas(Drawing())
        touch = self.touch(10, 20)

        canvas._pencil_down(touch)

        touch.x = 30
        touch.y = 40
        touch.pos = (30, 40)

        result = canvas._pencil_move(touch)

        assert result is True
        assert canvas.current_stroke == [10, 20, 30, 40]

    def test_pencil_up(self):
        drawing = Drawing()
        canvas = DrawingCanvas(drawing)
        touch = self.touch(10, 20)

        canvas._pencil_down(touch)

        touch.x = 30
        touch.y = 40
        touch.pos = (30, 40)

        canvas._pencil_move(touch)
        result = canvas._pencil_up(touch)

        assert result is True
        assert len(drawing.strokes) == 1
        assert drawing.strokes[0].points == [10, 20, 30, 40]

    def test_reset_current_stroke(self):
        canvas = DrawingCanvas(Drawing())
        canvas.active_touch = self.touch()
        canvas.current_stroke = [1, 2, 3, 4]

        canvas._reset_current_stroke()

        assert canvas.active_touch is None
        assert canvas.current_stroke == []
        assert canvas.current_line is None

    def test_on_touch_down(self):
        canvas = DrawingCanvas(Drawing())
        touch = self.touch()

        result = canvas.on_touch_down(touch)

        assert result is True
        assert canvas.active_touch is touch

    def test_on_touch_move(self):
        canvas = DrawingCanvas(Drawing())
        touch = self.touch(10, 20)

        canvas.on_touch_down(touch)

        touch.x = 30
        touch.y = 40
        touch.pos = (30, 40)

        result = canvas.on_touch_move(touch)

        assert result is True
        assert canvas.current_stroke == [10, 20, 30, 40]

    def test_on_touch_up(self):
        drawing = Drawing()
        canvas = DrawingCanvas(drawing)
        touch = self.touch(10, 20)

        canvas.on_touch_down(touch)

        touch.x = 30
        touch.y = 40
        touch.pos = (30, 40)

        canvas.on_touch_move(touch)
        result = canvas.on_touch_up(touch)

        assert result is True
        assert len(drawing.strokes) == 1
        assert drawing.strokes[0].points == [10, 20, 30, 40]
