# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `notify_model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `notify_model_is_changed` method must be overridden.
from os import path, linesep
from typing import Tuple

from notes_app.utils.time import format_epoch

# TODO remove FALLBACK_NOTES_FILE_PATH ref. to local disk file
FALLBACK_NOTES_FILE_PATH = "C:\\Users\\pavel.prudky\\PycharmProjects\\notes_app\\notes_app\\assets\\sample.txt"
DEFAULT_MODEL_STORE_FILE_NAME = "model.json"
LAST_UPDATED_ON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_additional_attributes_from_file_path(file_path: str) -> Tuple[int, str]:
    return (
        path.getsize(file_path),
        format_epoch(
            format=LAST_UPDATED_ON_TIME_FORMAT, epoch_time=path.getmtime(file_path)
        ),
    )


class NotesModel:
    """
    The NotesModel class is a data model implementation. The model stores
    the values of the variables related to the storage file metadata. The model provides an
    interface through which to work with stored values. The model contains
    methods for registration, deletion and notification observers.
    """

    def __init__(self, store, notes_file_path: str = None):
        self.store = store(filename=DEFAULT_MODEL_STORE_FILE_NAME)
        self._set_store_default_value_if_empty()

        if notes_file_path and path.exists(notes_file_path):
            self._file_path = notes_file_path
            (
                self._file_size,
                self._last_updated_on,
            ) = get_additional_attributes_from_file_path(self._file_path)

        elif self.store.get("_file_path")["value"] and path.exists(
                self.store.get("_file_path")["value"]
        ):
            self._file_path = self.store.get("_file_path")["value"]
            self._file_size = self.store.get("_file_size")["value"]
            self._last_updated_on = self.store.get("_last_updated_on")["value"]

        else:
            self._file_path = FALLBACK_NOTES_FILE_PATH
            (
                self._file_size,
                self._last_updated_on,
            ) = get_additional_attributes_from_file_path(self._file_path)

        self.observers = []

    def __repr__(self):
        return {
            "_file_path": self.file_path,
            "_file_size": self._file_size,
            "_last_updated_on": self._last_updated_on,
        }

    def _set_store_default_value_if_empty(self):
        if not self.store.exists('_file_path') or self.store.get("_file_path")["value"] is None:
            self.store.put("_file_path", value=FALLBACK_NOTES_FILE_PATH)

        if not self.store.exists('_file_size') or self.store.get("_file_size")["value"] is None:
            self.store.put("_file_size", value=0)

        if not self.store.exists('_last_updated_on') or self.store.get("_last_updated_on")["value"] is None:
            self.store.put("_last_updated_on", value="")

    @staticmethod
    def _get_attribute_to_formatted_name_map():
        return {
            "_file_path": "File path",
            "_file_size": "File size (bytes)",
            "_last_updated_on": "Last updated on",
        }

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value
        self.notify_observers()

    @property
    def file_size(self):
        return self._file_size

    @file_size.setter
    def file_size(self, value):
        self._file_size = value
        self.notify_observers()

    @property
    def last_updated_on(self):
        return self._last_updated_on

    @last_updated_on.setter
    def last_updated_on(self, value):
        self._last_updated_on = format_epoch(
            format=LAST_UPDATED_ON_TIME_FORMAT, epoch_time=value
        )
        self.notify_observers()

    @property
    def formatted(self):
        all_instance_attributes = list(self.__dict__.items())
        attribute_to_formatted_name_map = (
            NotesModel._get_attribute_to_formatted_name_map()
        )

        return linesep.join(
            f"{attribute_to_formatted_name_map[map_item[0]]} : {map_item[1]}"
            for map_item in all_instance_attributes
            if map_item[0] in attribute_to_formatted_name_map
        )

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for o in self.observers:
            o.notify_model_is_changed()

    def dump(self):
        self.store.put("_file_path", value=self._file_path)
        self.store.put("_file_size", value=self._file_size)
        self.store.put("_last_updated_on", value=self._last_updated_on)
