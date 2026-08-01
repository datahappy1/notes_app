from kivy.uix.modalview import ModalView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from notes_app.view.drawing_canvas import DrawingCanvas


class DrawingWindow(ModalView):
    def __init__(self, section, drawing_service, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False

        self.section = section
        self.service = drawing_service
        self.drawing = self.service.load(section)

        root = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding="10dp",
        )

        self.canvas_widget = DrawingCanvas(
            drawing=self.drawing,
            size_hint=(1, 1),
        )

        buttons = MDBoxLayout(
            adaptive_height=True,
            spacing="10dp",
        )

        cancel_btn = MDRaisedButton(text="Cancel")
        cancel_btn.bind(on_release=lambda *_: self.dismiss())

        save_btn = MDRaisedButton(text="Save")
        save_btn.bind(on_release=self.save)

        buttons.add_widget(cancel_btn)
        buttons.add_widget(save_btn)

        root.add_widget(self.canvas_widget)
        root.add_widget(buttons)

        self.add_widget(root)

    def save(self, *args):
        self.service.save(self.section, self.drawing)

        self.canvas_widget.export_to_png(
            str(self.service.png_path(self.section))
        )

        self.dismiss()
