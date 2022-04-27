# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `notify_model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `notify_model_is_changed` method must be overridden.
import base64
import json
from os import path, linesep, getcwd

from notes_app.utils.time import format_epoch

MODEL_STORAGE_FILE_PATH = f"{getcwd()}/model/myscreen.model"
FALLBACK_NOTES_FILE_PATH = f"{getcwd()}/assets/sample.txt"
LAST_UPDATED_ON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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
        self._file_path = self.safe_load().get("_file_path") or FALLBACK_NOTES_FILE_PATH
        self._file_size = self.safe_load().get("_file_size") or path.getsize(self._file_path)
        self._last_updated_on = self.safe_load().get("_last_updated_on") or format_epoch(
            format=LAST_UPDATED_ON_TIME_FORMAT,
            epoch_time=path.getmtime(self._file_path),
        )
        self.observers = []

    def __repr__(self):
        return {
            "_file_path": self.file_path,
            "_file_size": self._file_size,
            "_last_updated_on": self._last_updated_on,
        }

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
            MyScreenModel._get_attribute_to_formatted_name_map()
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

    def dump_encoded(self):
        json_data = json.dumps(self.__repr__()).encode()
        encoded_data = base64.encodebytes(json_data)

        with open(MODEL_STORAGE_FILE_PATH, "wb") as model_file:
            model_file.write(encoded_data)

    def safe_load(self):
        try:
            with open(MODEL_STORAGE_FILE_PATH, "rb") as model_file:
                decoded_data = base64.decodebytes(model_file.read())
                json_data = json.loads(decoded_data)
                return json_data
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
