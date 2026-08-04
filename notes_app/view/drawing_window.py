from kivy.uix.modalview import ModalView

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard

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

        toolbar = MDCard(
            size_hint_y=None,
            height="64dp",
            radius=[12, 12, 12, 12],
            elevation=4,
            md_bg_color=(0.08, 0.09, 0.11, 1),
        )

        buttons = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            padding=("10dp", "8dp"),
        )

        close_btn = MDRaisedButton(
            text="Close",
            size_hint=(None, None),
            size=("90dp", "48dp"),
            pos_hint={"center_y": 0.5},
        )
        close_btn.bind(on_release=lambda *_: self.dismiss())

        save_btn = MDRaisedButton(
            text="Save",
            size_hint=(None, None),
            size=("90dp", "48dp"),
            pos_hint={"center_y": 0.5},
        )
        save_btn.bind(on_release=self.save)

        buttons.add_widget(close_btn)
        buttons.add_widget(save_btn)

        # Separator
        buttons.add_widget(self.create_separator())

        black_pen_button = self.get_colored_pen_button(
            color=(0, 0, 0, 1)
        )
        red_pen_button = self.get_colored_pen_button(
            color=(1, 0, 0, 1)
        )
        blue_pen_button = self.get_colored_pen_button(
            color=(0, 0, 1, 1)
        )
        green_pen_button = self.get_colored_pen_button(
            color=(0, 0.5, 0, 1)
        )
        yellow_pen_button = self.get_colored_pen_button(
            color=(1, 1, 0, 1)
        )

        self.color_buttons = [
            black_pen_button,
            red_pen_button,
            blue_pen_button,
            green_pen_button,
            yellow_pen_button,
        ]

        buttons.add_widget(black_pen_button)
        buttons.add_widget(red_pen_button)
        buttons.add_widget(blue_pen_button)
        buttons.add_widget(green_pen_button)
        buttons.add_widget(yellow_pen_button)

        buttons.add_widget(self.create_separator())

        clear_button = MDIconButton(
            icon="broom",
            theme_icon_color="Custom",
            icon_color=(0.65, 0.65, 0.65, 1),
            size_hint=(None, None),
            size=("48dp", "48dp"),
            pos_hint={"center_y": 0.5},
        )
        clear_button.bind(
            on_release=lambda *_: self.canvas_widget.clear()
        )

        undo_button = MDIconButton(
            icon="undo-variant",
            theme_icon_color="Custom",
            icon_color=(0.65, 0.65, 0.65, 1),
            size_hint=(None, None),
            size=("48dp", "48dp"),
            pos_hint={"center_y": 0.5},
        )
        undo_button.bind(
            on_release=lambda *_: self.canvas_widget.undo()
        )

        buttons.add_widget(clear_button)
        buttons.add_widget(undo_button)

        toolbar.add_widget(buttons)

        root.add_widget(self.canvas_widget)
        root.add_widget(toolbar)

        self.add_widget(root)

    def create_separator(self):
        """Create a small vertical separator for the toolbar."""
        return MDBoxLayout(
            size_hint=(None, None),
            size=("1dp", "32dp"),
            pos_hint={"center_y": 0.5},
            md_bg_color=(0.3, 0.32, 0.35, 1),
        )

    def get_colored_pen_button(self, color):
        colored_pen_button = MDIconButton(
            icon="pencil-circle-outline",
            theme_icon_color="Custom",
            icon_color=color,
            size_hint=(None, None),
            size=("48dp", "48dp"),
            pos_hint={"center_y": 0.5},
        )

        colored_pen_button.bind(
            on_release=lambda *_: self.select_icon(
                colored_pen_button,
                color,
            )
        )

        return colored_pen_button

    def select_icon(self, button, color):
        self.canvas_widget.set_color(color)

        # Remove selection outline from all color buttons.
        for color_button in self.color_buttons:
            color_button.icon = "pencil-circle-outline"

        # Add selection outline to the selected button.
        button.icon = "pencil-circle"

    def save(self, *args):
        self.service.save(self.section, self.drawing)

        self.canvas_widget.export_to_png(
            str(self.service.png_path(self.section))
        )

