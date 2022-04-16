# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `notify_model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `notify_model_is_changed` method must be overridden.
import time
from os import path, linesep

from notes_app.settings import FALLBACK_NOTES_FILE_PATH

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

    def __init__(self, settings):
        self._file_path = settings.notes_file_path or FALLBACK_NOTES_FILE_PATH
        self._file_size = path.getsize(self._file_path)
        self._last_updated_on = MyScreenModel.format_epoch(
            path.getmtime(self._file_path)
        )
        self.observers = []

    @staticmethod
    def format_epoch(epoch_time):
        return time.strftime(LAST_UPDATED_ON_TIME_FORMAT, time.localtime(epoch_time))

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
        self._last_updated_on = MyScreenModel.format_epoch(value)
        self.notify_observers()

    @property
    def formatted(self):
        all_instance_attributes = list(self.__dict__.items())
        attribute_to_formatted_name_map = {
            "_file_path": "File path",
            "_file_size": "File size (bytes)",
            "_last_updated_on": "Last updated on",
        }

        return linesep.join(
            [
                f"{attribute_to_formatted_name_map[map_item[0]]} : {map_item[1]}"
                for map_item in all_instance_attributes
                if map_item[0] in attribute_to_formatted_name_map
            ]
        )

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for o in self.observers:
            o.notify_model_is_changed()
