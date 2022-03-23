import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivymd.uix.screen import MDScreen
from notes_app.settings import APP_STARTUP_FILE_PATH

from notes_app.utils.observer import Observer


class MyScreenView(MDScreen, Observer):
    """"
    A class that implements the visual presentation `MyScreenModel`.

    """

    # <Controller.myscreen_controller.MyScreenController object>.
    controller = ObjectProperty()
    # <Model.myscreen.MyScreenModel object>.
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)  # register the view as an observer

    def set_c(self, focus, value):
        if not focus:
            self.controller.set_c(value)

    def set_d(self, focus, value):
        if not focus:
            self.controller.set_d(value)

    def model_is_changed(self):
        """
        The method is called when the model changes.
        Requests and displays the value of the sum.
        """

        self.ids.result.text = str(self.model.sum)

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

        def __init__(self, model, **kwargs):
            super(MyScreenView.MainWindow, self).__init__()
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


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
