from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from notes_app.settings import APP_STARTUP_FILE_PATH
from notes_app.view.myscreen import MyScreenView


class MyScreenController:
    """
    The `MyScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.

    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        """
        The constructor takes a reference to the model.
        The constructor creates the view.
        """

        self.model = model
        self.view = MyScreenView(controller=self, model=self.model)


class MainWindow(BoxLayout):
    open_button = ObjectProperty()
    save_button = ObjectProperty()
    search_button = ObjectProperty()
    text_view = ObjectProperty()

    def __init__(self, model, **kwargs):
        super(MainWindow, self).__init__()
        self.clipboard_text = ""
        self.filepath = ""
        self.model = model
        self.view = MyScreenView(controller=self, model=self.model)
        self.on_startup()

    def on_open(self, *args):
        content = self.view.OpenDialog(open_file=self.open_file,
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
        self.view.cancel_dialog()

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

    def get_screen(self):
        """The method creates get the view."""

        return self.view

    def set_c(self, value):
        """
        When finished editing the data entry field for `C`, the controller
        changes the `c` property of the model.
        """

        self.model.c = value

    def set_d(self, value):
        """
        When finished editing the data entry field for `D`, the controller
        changes the `d` property of the model.
        """

        self.model.d = value
