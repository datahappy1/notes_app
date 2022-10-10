from datetime import datetime
from notes_app.view.notes_view import NotesView


class NotesController:
    """
    The `NotesController` class represents a controller implementation.
    Coordinates work of the view with the model.

    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, settings, model, defaults):
        """
        The constructor takes a reference to the model.
        The constructor creates the view.
        """
        self.defaults = defaults
        self.model = model
        self._generate_default_file_if_not_exists()

        self.view = NotesView(
            settings=settings, controller=self, model=self.model, defaults=self.defaults
        )

    def _generate_default_file_if_not_exists(self) -> None:
        """
        when the model is not associated with any existing file to store the notes in,
        such default file gets automatically created
        """
        if not self.model.file_path_exists:
            with open(file=self.defaults.DEFAULT_NOTES_FILE_NAME, mode="w", encoding="utf8") as f:
                f.write(self.defaults.DEFAULT_NOTES_FILE_CONTENT)

    def set_file_path(self, file_path) -> None:
        self.model.file_path = file_path
        self.model.update()
        self.model.dump()

    def read_file_data(self, file_path=None) -> str:
        f = open(file_path or self.model.file_path, "r", encoding="utf8")
        s = f.read()
        f.close()
        return s

    def save_file_data(self, data) -> None:
        """
        save_file_data saves provided data to the file with location set in model.file_path
        """
        if len(data) == 0:
            return
        try:
            with open(self.model.file_path, "w", encoding="utf8") as f:
                f.write(data)
        except Exception as exc:
            # another attempt at writing at least a dump file
            with open(f"__dump__{datetime.now():%Y_%m_%d_%H_%M_%S}", "w", encoding="utf8") as f:
                f.write(data)
            raise exc

        self.model.update()
        self.model.dump()

    def get_screen(self):
        """
        The method creates get the view.
        """
        return self.view
