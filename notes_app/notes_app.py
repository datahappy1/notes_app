from kivy.app import App
from kivy.properties import *
from kivy.uix.boxlayout import *
from kivy.uix.floatlayout import *
from kivy.uix.popup import Popup

BASE_FILE_PATH = "C:\\Users\pavel.prudky\\agents_with_default_profiles.txt"


class NotesApp(App):
    def __init__(self):
        App.__init__(self)

    def build(self):
        return MainWindow()


class OpenDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MainWindow(BoxLayout):
    open_button = ObjectProperty()
    save_button = ObjectProperty()
    text_view = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__()
        self.clipboard_text = ""
        self.filepath = ""

    def on_open(self, *args):
        content = OpenDialog(open_file=self.open_file,
                             cancel=self.cancel_dialog)
        self._popup = Popup(title="Open File", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def open_file(self, path, filename):
        self.filepath = filename[0]
        f = open(self.filepath, 'r')
        s = f.read()
        self.text_view.text = s
        f.close()
        self.cancel_dialog()

    def cancel_dialog(self):
        self._popup.dismiss()

    def on_save(self, *args):
        f = open(self.filepath, 'w')
        f.write(self.text_view.text)
        f.close()


if __name__ == '__main__':
    NotesApp().run()
