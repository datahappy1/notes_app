# The model implements the observer pattern. This means that the class must
# support adding, removing, and alerting observers. In this case, the model is
# completely independent of controllers and views. It is important that all
# registered observers implement a specific method that will be called by the
# model when they are notified (in this case, it is the `notify_model_is_changed`
# method). For this, observers must be descendants of an abstract class,
# inheriting which, the `notify_model_is_changed` method must be overridden.
import time
from os import path, linesep

from notes_app.settings import APP_STARTUP_FILE_PATH

LAST_UPDATED_ON_VALUE_PLACEHOLDER = "-"
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
        self.filePath = APP_STARTUP_FILE_PATH
        self.fileSize = path.getsize(self.filePath)
        self.lastUpdatedOn = LAST_UPDATED_ON_VALUE_PLACEHOLDER
        self.observers = []

    @property
    def file_path(self):
        return self.filePath

    @file_path.setter
    def file_path(self, value):
        self.filePath = value
        self.notify_observers()

    @property
    def file_size(self):
        return self.fileSize

    @file_size.setter
    def file_size(self, value):
        self.fileSize = value
        self.notify_observers()

    @property
    def last_updated_on(self):
        return self.lastUpdatedOn

    @last_updated_on.setter
    def last_updated_on(self, value):
        if value:
            self.lastUpdatedOn = time.strftime(
                LAST_UPDATED_ON_TIME_FORMAT, time.localtime(value)
            )
        else:
            self.lastUpdatedOn = LAST_UPDATED_ON_VALUE_PLACEHOLDER
        self.notify_observers()

    @property
    def formatted(self):
        all_instance_attributes = list(self.__dict__.items())
        attribute_to_formatted_name_map = {
            "filePath": "file path",
            "fileSize": "file size",
            "lastUpdatedOn": "last updated on"
        }

        return linesep.join(
            [f"{attribute_to_formatted_name_map[map_item[0]]} : {map_item[1]}"
             for map_item in all_instance_attributes
             if map_item[0] in attribute_to_formatted_name_map]
        )

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for o in self.observers:
            o.notify_model_is_changed()
