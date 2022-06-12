from notes_app.diff import merge_strings
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
        self._generate_default_file_if_file_path_missing()

        self.view = NotesView(
            settings=settings, controller=self, model=self.model, defaults=self.defaults
        )

    def _generate_default_file_if_file_path_missing(self):
        """
        when the model is not associated with any file to store notes in,
        it gets automatically created during the controller initialization
        """
        if (
            not self.model.store.exists("_file_path")
            or self.model.store.get("_file_path")["value"] is None
            or (
                any(
                    x == 0
                    for x in [
                        self.model.store.get("_file_size")["value"],
                        self.model.store.get("_last_updated_on")["value"],
                    ]
                )
            )
        ):
            with open(file=self.defaults.DEFAULT_NOTES_FILE_NAME, mode="w") as f:
                f.write(self.defaults.DEFAULT_NOTES_FILE_CONTENT)

    def set_file_path(self, file_path):
        self.model.file_path = file_path
        self.model.update()
        self.model.dump()

    def read_file_data(self, file_path=None):
        f = open(file_path or self.model.file_path, "r")
        s = f.read()
        f.close()
        return s

    def save_file_data(self, data):
        """
        save_file_data saves provided data to the file with location set in model.file_path,
        if the file was updated by another instance of the notes app, check if model property external_update
        evaluates to True, the code-path goes through difflib merge_string to save the merged string data to the file
        """
        if self.model.external_update:
            f = open(self.model.file_path, "r")
            # in case deleted file content fallback to empty string
            before = f.read() or ""
            f.close()

            data = merge_strings(before=before, after=data)

        f = open(self.model.file_path, "w")
        f.write(data)
        f.close()

        self.model.update()
        self.model.dump()

    def get_screen(self):
        """The method creates get the view."""
        return self.view
