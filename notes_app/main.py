from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel
from notes_app.settings import APP_STARTUP_FILE_PATH


class OpenDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MainWindow(BoxLayout):
    open_button = ObjectProperty()
    save_button = ObjectProperty()
    search_button = ObjectProperty()
    text_view = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__()
        self.clipboard_text = ""
        self.filepath = ""
        self.on_startup()

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

    def on_search(self, *args):
        pass

    def on_startup(self):
        self.filepath = APP_STARTUP_FILE_PATH
        f = open(self.filepath, 'r')
        s = f.read()
        self.text_view.text = s
        f.close()


class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = MyScreenModel()
        self.controller = MyScreenController(self.model)

    def build(self):
        return MainWindow()


NotesApp().run()
