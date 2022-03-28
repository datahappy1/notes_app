# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `model_is_changed` method must be overridden.
from datetime import datetime

from notes_app.settings import APP_STARTUP_FILE_PATH


class NotesMetaData:
    def __init__(self, updated_on, file_path):
        self.updatedOn: str = updated_on
        self.filePath: str = file_path
        self.byteCount: int = self._get_byte_count()

    def _get_byte_count(self):
        with open(self.filePath, mode="r") as f:
            return len(f.read())


class MyScreenModel:
    """
    The MyScreenModel class is a data model implementation. The model stores
    the values of the variables `c`, `d` and their sum. The model provides an
    interface through which to work with stored values. The model contains
    methods for registration, deletion and notification observers.

    The model is (primarily) responsible for the logic of the application.
    MyScreenModel class task is to add two numbers.
    """

    def __init__(self):
        self._metadata = NotesMetaData(
            updated_on=str(datetime.now()),
            file_path=APP_STARTUP_FILE_PATH
        )
        self._observers = []

    def __str__(self):
        return str(self._metadata.__dict__)

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for o in self._observers:
            o.model_is_changed()
