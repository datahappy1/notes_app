import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivymd.uix.screen import MDScreen

from notes_app.utils.observer import Observer


class OpenDialog(FloatLayout):
    open_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save_file = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MyScreenView(BoxLayout, MDScreen, Observer):
    """"
    A class that implements the visual presentation `MyScreenModel`.

    """
    controller = ObjectProperty()
    model = ObjectProperty()

    open_button = ObjectProperty()
    save_button = ObjectProperty()
    search_button = ObjectProperty()
    text_view = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)  # register the view as an observer
        self.open_dialog = OpenDialog()
        self.save_dialog = SaveDialog()
        self.on_startup()

    def model_is_changed(self):
        """
        The method is called when the model changes.
        Requests and displays the value of the sum.
        """
        self.ids.result.text = str(self.model.sum)
        # TODO here it fails on save -> we update back through the kv

    def on_startup(self):
        self.text_view.text = self.controller.read_file_data()

    def open_file(self, path, filename):
        self.file_path = filename[0]
        f = open(self.file_path, 'r')
        s = f.read()
        self.text_view.text = s
        f.close()
        self.cancel_dialog()

    def cancel_dialog(self):
        self._popup.dismiss()

    def on_open(self, *args):
        content = OpenDialog(open_file=self.open_file,
                             cancel=self.cancel_dialog)
        self._popup = Popup(title="Open File", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def on_save(self, *args):
        self.controller.save_file_data(data=self.text_view.text)

    def on_search(self, *args):
        pass


Builder.load_file(os.path.join(os.path.dirname(__file__), "myscreen.kv"))
