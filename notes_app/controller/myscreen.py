from datetime import datetime

from notes_app.model.myscreen import NotesMetaData
from notes_app.view.myscreen import MyScreenView
from notes_app.settings import APP_STARTUP_FILE_PATH


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
        self.file_path = APP_STARTUP_FILE_PATH
        self.model = model
        self.view = MyScreenView(controller=self, model=self.model)

    def _update_metadata(self):
        self.model.metadata = NotesMetaData(
            updated_on=str(datetime.now()),
            file_path=self.file_path,
        )

    def set_file_path(self, file_path):
        self.file_path = file_path
        self._update_metadata()

    def read_file_data(self, file_path=None):
        f = open(file_path or self.file_path, 'r')
        s = f.read()
        f.close()
        return s

    def save_file_data(self, data):
        f = open(self.file_path, 'w')
        f.write(data)
        f.close()

        self._update_metadata()
        print(self.model.metadata)

    def get_screen(self):
        """The method creates get the view."""
        return self.view
