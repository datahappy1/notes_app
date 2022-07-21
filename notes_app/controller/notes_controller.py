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
        self._defaults = defaults
        self._model = model
        self._generate_default_file_if_not_exists()

        self._view = NotesView(
            settings=settings, controller=self, model=self._model, defaults=self._defaults
        )

    def _generate_default_file_if_not_exists(self) -> None:
        """
        when the model is not associated with any existing file to store the notes in,
        such default file gets automatically created
        """
        if not self._model.file_path_exists:
            with open(file=self._defaults.DEFAULT_NOTES_FILE_NAME, mode="w") as f:
                f.write(self._defaults.DEFAULT_NOTES_FILE_CONTENT)

    def set_file_path(self, file_path) -> None:
        self._model.file_path = file_path
        self._model.update()
        self._model.dump()

    def read_file_data(self, file_path=None) -> str:
        f = open(file_path or self._model.file_path, "r")
        s = f.read()
        f.close()
        return s

    def save_file_data(self, data) -> None:
        """
        save_file_data saves provided data to the file with location set in model.file_path
        """
        f = open(self._model.file_path, "w")
        f.write(data)
        f.close()

        self._model.update()
        self._model.dump()

    def get_screen(self):
        """
        The method creates get the view.
        """
        return self._view
