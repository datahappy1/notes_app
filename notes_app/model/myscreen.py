# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `model_is_changed` method must be overridden.
import time
from os import path, linesep

from notes_app.settings import APP_STARTUP_FILE_PATH


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
        self._filePath = APP_STARTUP_FILE_PATH
        self._fileSize = path.getsize(self._filePath)
        self._lastUpdatedOn = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(path.getmtime(self._filePath)))
        self._observers = []

    @property
    def file_path(self):
        return self._filePath

    @file_path.setter
    def file_path(self, value):
        self._filePath = value
        self.notify_observers()

    @property
    def file_size(self):
        return self._fileSize

    @file_size.setter
    def file_size(self, value):
        self._fileSize = value
        self.notify_observers()

    @property
    def last_updated_on(self):
        return self._lastUpdatedOn

    @last_updated_on.setter
    def last_updated_on(self, value):
        self._lastUpdatedOn = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
        self.notify_observers()

    def get_formatted(self):
        _all_instance_attributes = list(self.__dict__.items())
        _attribute_name_mapping = {
            "_filePath": "file path",
            "_fileSize": "file size",
            "_lastUpdatedOn": "last updated on"
        }
        _filtered_instance_attributes = [
            item for item in _all_instance_attributes if item[0] in _attribute_name_mapping
        ]

        return linesep.join(
            [f"{_attribute_name_mapping[item[0]]} : {item[1]}" for item in _filtered_instance_attributes]
        )

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for o in self._observers:
            o.model_is_changed()
