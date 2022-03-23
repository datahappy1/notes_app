from kivy.uix.popup import Popup

from notes_app.settings import APP_STARTUP_FILE_PATH
from notes_app.view.main_screen import MainScreenView


class MainScreenController:
    def __init__(self, model, **kwargs):
        self._model = model
        self._view = MainScreenView(controller=self, model=self._model)
        self.clipboard_text = ""
        self.filepath = APP_STARTUP_FILE_PATH
        self._popup = None

        print(self._view, self._view.text_view)
        self.on_startup()

    def on_open(self, *args):
        content = self._view.OpenDialog(open_file=self.open_file, cancel=self.cancel_dialog)
        self._popup = Popup(title="Open File", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def open_file(self, path, filename):
        self.filepath = filename[0]
        f = open(self.filepath, 'r')
        s = f.read()
        self._view.text_view.text = s
        f.close()
        self.cancel_dialog()

    def cancel_dialog(self):
        self._popup.dismiss()

    def on_save(self, *args):
        f = open(self.filepath, 'w')
        f.write(self._view.text_view.text)
        f.close()

    def on_search(self, *args):
        pass

    def on_startup(self):
        f = open(self.filepath, 'r')
        s = f.read()
        self._view.text_view.text = s
        f.close()

    def get_screen(self):
        return self._view

    def set_d(self, value):
        self._model.d = value
