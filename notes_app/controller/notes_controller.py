import time

from notes_app.utils.diff import merge_strings
from notes_app.utils.path import (
    get_file_size,
    get_file_updated_timestamp_as_epoch,
)
from notes_app.view.notes_view import NotesView


class NotesController:
    """
    The `NotesController` class represents a controller implementation.
    Coordinates work of the view with the model.

    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, settings, model):
        """
        The constructor takes a reference to the model.
        The constructor creates the view.
        """
        self.model = model
        self.view = NotesView(settings=settings, controller=self, model=self.model)

    def set_file_path(self, file_path):
        self.model.file_path = file_path
        self.model.file_size = get_file_size(file_path)
        self.model.last_updated_on = get_file_updated_timestamp_as_epoch(file_path)
        self.model.dump()

    def read_file_data(self, file_path=None):
        f = open(file_path or self.model.file_path, "r")
        s = f.read()
        f.close()
        return s

    def _check_is_external_update(self):
        """
        _check_is_external_update method evaluates whether the file last updated
        timestamps indicate it was updated from another app instance ( ex. DropBox shared folder )
        by comparing the stored last_updated_on timestamp and the filesystem last update timestamp
        using get_file_updated_timestamp_as_epoch
        """
        return (
            get_file_updated_timestamp_as_epoch(self.model.file_path)
            > self.model.last_updated_on
        )

    def save_file_data(self, data) -> bool:
        """
        save_file_data saves provided data to the file with location set in model.file_path
        if the file was updated by another instance of the notes app, check_is_external_update
        evaluates to True, the code-path goes through difflib merge_string and save_file_data method
        returns True. If no external update was evaluated, this method returns False.
        """
        is_external_update = self._check_is_external_update()
        if is_external_update:
            f = open(self.model.file_path, "r")
            # in case deleted file content fallback to empty string
            before = f.read() or ""
            f.close()

            data = merge_strings(before=before, after=data)

        f = open(self.model.file_path, "w")
        f.write(data)
        f.close()

        self.model.file_size = get_file_size(self.model.file_path)
        # we first save the file and then set the last_updated_on timestamp to the model,
        # this guarantees that the condition: get_file_updated_timestamp_as_epoch(self.model.file_path) > self.model.last_updated_on_as_epoch
        # makes sense even if we don't manage to write the file and store the last_updated_on timestamp in the same second
        # because of growing file size or other IO dependencies
        self.model.last_updated_on = time.time()
        self.model.dump()

        return is_external_update

    def get_screen(self):
        """The method creates get the view."""
        return self.view
