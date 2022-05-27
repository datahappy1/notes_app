# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `notify_model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `notify_model_is_changed` method must be overridden.
import json
from os import linesep, path

from notes_app.utils.file import SECTION_FILE_SEPARATOR
from notes_app.utils.time import format_epoch

DEFAULT_NOTES_FILE_NAME = "my_first_file.txt"
DEFAULT_NOTES_FILE_CONTENT = f"{SECTION_FILE_SEPARATOR.format(name='first')} Your first section. Here you can write your notes."

DEFAULT_MODEL_STORE_FILE_NAME = "file_metadata.json"
LAST_UPDATED_ON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_file_size(file_path):
    return path.getsize(file_path)


def get_formatted_epoch(file_path):
    return format_epoch(
        format=LAST_UPDATED_ON_TIME_FORMAT, epoch_time=path.getmtime(file_path)
    )


class DefaultNotesFile:
    def __init__(self, notes_file_name=None, notes_file_content=None):
        self._default_notes_file_name = notes_file_name or DEFAULT_NOTES_FILE_NAME
        self._default_notes_file_content = (
            notes_file_content or DEFAULT_NOTES_FILE_CONTENT
        )

    @property
    def default_notes_file_name(self):
        return self._default_notes_file_name

    @property
    def default_notes_file_content(self):
        return self._default_notes_file_content

    def generate(self) -> None:
        with open(file=self.default_notes_file_name, mode="w") as f:
            f.write(self._default_notes_file_content)


class NotesModel:
    """
    The NotesModel class is a data model implementation. The model stores
    the values of the variables related to the storage file metadata. The model provides an
    interface through which to work with stored values. The model contains
    methods for registration, deletion and notification observers.
    """

    def __init__(self, store, **kwargs):
        self.store = store(filename=DEFAULT_MODEL_STORE_FILE_NAME)
        self._default_notes_file = DefaultNotesFile(**kwargs)
        self._generate_default_file_if_file_path_missing()
        self._set_missing_store_defaults()

        self._file_path = self.store.get("_file_path")["value"]
        self._file_size = self.store.get("_file_size")["value"]
        self._last_updated_on = self.store.get("_last_updated_on")["value"]

        self.observers = []

    def __repr__(self):
        return json.dumps(
            {
                "_file_path": self.file_path,
                "_file_size": self._file_size,
                "_last_updated_on": self._last_updated_on,
            }
        )

    def _generate_default_file_if_file_path_missing(self):
        if (
                not self.store.exists("_file_path")
                or self.store.get("_file_path")["value"] is None
                or not path.exists(self.store.get("_file_path")["value"])
        ):
            self._default_notes_file.generate()

    def _set_missing_store_defaults(self):
        if (
                not self.store.exists("_file_path")
                or self.store.get("_file_path")["value"] is None
                or not path.exists(self.store.get("_file_path")["value"])
        ):
            self.store.put(
                "_file_path", value=self._default_notes_file.default_notes_file_name
            )

        if (
                not self.store.exists("_file_size")
                or self.store.get("_file_size")["value"] is None
        ):
            self.store.put(
                "_file_size",
                value=get_file_size(file_path=self.store.get("_file_path")["value"]),
            )

        if (
                not self.store.exists("_last_updated_on")
                or self.store.get("_last_updated_on")["value"] is None
        ):
            self.store.put(
                "_last_updated_on",
                value=get_formatted_epoch(
                    file_path=self.store.get("_file_path")["value"]
                ),
            )

    @staticmethod
    def _get_attribute_to_formatted_name_map():
        return {
            "_file_path": "File",
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
