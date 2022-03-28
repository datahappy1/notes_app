from kivymd.app import MDApp

from notes_app.controller.myscreen import MyScreenController
from notes_app.model.myscreen import MyScreenModel


class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = MyScreenModel()
        self.controller = MyScreenController(self.model)

    def build(self):
        return self.controller.get_screen()


NotesApp().run()