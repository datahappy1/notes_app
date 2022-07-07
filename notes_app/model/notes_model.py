# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `notify_model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `notify_model_is_changed` method must be overridden.
import json
import time
from os import linesep, path

GENERAL_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_local_epoch(format: str, epoch_time: int) -> str:
    """
    format epoch in local time based on provided format
    """
    return time.strftime(format, time.localtime(epoch_time))


def get_current_epoch() -> int:
    """
    get_current_epoch
    """
    return int(time.time())


def get_file_updated_timestamp_as_epoch(file_path: str) -> int:
    """
    get file updated timestamp as epoch
    """
    return int(path.getmtime(file_path))


class NotesModel:
    """
    The NotesModel class is a data model implementation. The model stores
    the values of the variables related to the storage file metadata. The model provides an
    interface through which to work with stored values. The model contains
    methods for registration, deletion and notification observers.
    """

    def __init__(self, store, defaults):
        self.defaults = defaults
        self.store = store(filename=self.defaults.DEFAULT_MODEL_STORE_FILE_NAME)

        self._set_missing_store_defaults()

        self._file_path = self.store.get("_file_path")["value"]
        self._file_size = self.store.get("_file_size")["value"]
        self._last_updated_on = self.store.get("_last_updated_on")["value"]

        self.observers = []

    def __repr__(self):
        return json.dumps(
            {
                "File": self.file_path,
                "File size (bytes)": self._file_size,
                "Last updated on": format_local_epoch(
                    format=GENERAL_DATE_TIME_FORMAT, epoch_time=self._last_updated_on
                ),
            }
        )

    def _set_missing_store_defaults(self):
        if (
            not self.store.exists("_file_path")
            or self.store.get("_file_path")["value"] is None
        ):
            self.store.put("_file_path", value=self.defaults.DEFAULT_NOTES_FILE_NAME)
        if (
            not self.store.exists("_file_size")
            or self.store.get("_file_size")["value"] is None
        ):
            self.store.put("_file_size", value=0)

        if (
            not self.store.exists("_last_updated_on")
            or self.store.get("_last_updated_on")["value"] is None
        ):
            self.store.put("_last_updated_on", value=0)

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = str(value)

    @property
    def file_path_exists(self):
        return path.exists(self._file_path)

    @property
    def file_size(self):
        return self._file_size

    @property
    def last_updated_on(self):
        return self._last_updated_on

    @property
    def formatted(self):
        return linesep.join(
            [f"{x[0]} : {x[1]}" for x in json.loads(self.__repr__()).items()]
        )

    @property
    def external_update(self):
        return (
            get_file_updated_timestamp_as_epoch(self.file_path)
            > self.last_updated_on
            > 0
        )

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for o in self.observers:
            o.notify_model_is_changed()

    def update(self) -> None:
        """
        update file-path related file attributes and notify observers
        """
        self._file_size = path.getsize(self.file_path)
        self._last_updated_on = get_current_epoch()

        self.notify_observers()

    def dump(self) -> None:
        """
        dump model variables into store
        """
        self.store.put("_file_path", value=self._file_path)
        self.store.put("_file_size", value=self._file_size)
        self.store.put("_last_updated_on", value=self._last_updated_on)
