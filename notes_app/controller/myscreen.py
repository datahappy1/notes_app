import time
from os import path

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

    def set_file_path(self, file_path):
        self.model.file_path = file_path
        self.model.file_size = path.getsize(file_path)
        self.model.last_updated_on = path.getmtime(file_path)

    def read_file_data(self, file_path=None):
        f = open(file_path or self.model.file_path, "r")
        s = f.read()
        f.close()
        return s

    def save_file_data(self, data):
        f = open(self.model.file_path, "w")
        f.write(data)
        f.close()

        self.model.file_size = path.getsize(self.model.file_path)
        self.model.last_updated_on = time.time()

    def get_screen(self):
        """The method creates get the view."""
        return self.view
