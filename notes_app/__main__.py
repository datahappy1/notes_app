import kivy

kivy.require("2.0.0")

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout


class HomePage(GridLayout):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)

        self.cols = 1

        self.input = TextInput(multiline=True)
        self.add_widget(self.input)
        self.input.bind(on_text_validate=self.print_input)

    def print_input(self, value):
        print(value.text)


class MyApp(App):
    def build(self):
        return HomePage()


if __name__ == "__main__":
    MyApp().run()
