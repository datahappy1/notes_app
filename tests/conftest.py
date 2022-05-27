import json
import os
from os import getcwd

import pytest
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp

from notes_app.controller.notes_controller import NotesController
from notes_app.model.notes_model import DEFAULT_MODEL_STORE_FILE_NAME, NotesModel
from notes_app.utils.default_notes_file import DefaultNotesFile
from notes_app.utils.file import File
from notes_app.utils.settings import DEFAULT_SETTINGS_STORE_FILE_NAME, Settings

TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME = "my_first_file.txt"
TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH = getcwd()
TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH = f"{TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH}/{TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME}"
TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT = """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""

TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_NAME = "empty.txt"
TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_PATH = f"{TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH}/{TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_NAME}"
TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_CONTENT = """"""

default_notes_file = DefaultNotesFile()
default_notes_file.default_notes_file_name = TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME
default_notes_file.default_notes_file_content = TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT


def create_settings_file():
    with open(file=f"{getcwd()}/{DEFAULT_SETTINGS_STORE_FILE_NAME}", mode="w") as f:
        f.write(
            json.dumps(
                {
                    "font_name": {"value": "Roboto-Bold"},
                    "font_size": {"value": "14.0"},
                    "background_color": {"value": "blue"},
                    "foreground_color": {"value": "green"},
                }
            )
        )


def delete_settings_file():
    fp = f"{getcwd()}/{DEFAULT_SETTINGS_STORE_FILE_NAME}"
    if os.path.exists(fp):
        os.remove(fp)


def read_settings_file():
    with open(file=f"{getcwd()}/{DEFAULT_SETTINGS_STORE_FILE_NAME}", mode="r") as f:
        json_data = json.loads(f.read())
    return json_data


def create_model_file():
    with open(file=f"{getcwd()}/{DEFAULT_MODEL_STORE_FILE_NAME}", mode="w") as f:
        f.write(
            json.dumps(
                {
                    "_file_path": {"value": TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH},
                    "_file_size": {"value": 0},
                    "_last_updated_on": {"value": "2022-04-25 09:05:56"},
                }
            )
        )


def delete_model_file():
    fp = f"{getcwd()}/{DEFAULT_MODEL_STORE_FILE_NAME}"
    if os.path.exists(fp):
        os.remove(fp)


def read_model_file():
    with open(file=f"{getcwd()}/{DEFAULT_MODEL_STORE_FILE_NAME}", mode="r") as f:
        json_data = json.loads(f.read())
    return json_data


def create_default_notes_file():
    with open(file=TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH, mode="w") as notes_file:
        notes_file.write(TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT)


def delete_default_notes_file():
    if os.path.exists(TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH):
        os.remove(TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH)


def read_default_notes_file():
    with open(file=TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH, mode="r") as f:
        text_data = f.read()
    return text_data


def create_default_empty_notes_file():
    with open(file=TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_PATH, mode="w") as notes_file:
        notes_file.write(TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_CONTENT)


def delete_default_empty_notes_file():
    if os.path.exists(TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_PATH):
        os.remove(TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_PATH)


def read_default_empty_notes_file():
    with open(file=TEST_OVERRIDE_DEFAULT_NOTES_EMPTY_FILE_PATH, mode="r") as f:
        text_data = f.read()
    return text_data


@pytest.fixture(autouse=True)
def get_default_test_files_state():
    create_settings_file()
    create_model_file()
    # commented out on purpose since the model initializer creates the default notes file if needed
    # create_default_notes_file()
    create_default_empty_notes_file()
    yield
    delete_settings_file()
    delete_model_file()
    delete_default_notes_file()
    delete_default_empty_notes_file()


@pytest.fixture
def get_model():
    return NotesModel(store=JsonStore, default_file=default_notes_file)


@pytest.fixture()
def get_file():
    controller = NotesController(
        settings=Settings(store=JsonStore),
        model=NotesModel(store=JsonStore, default_file=default_notes_file),
    )

    file = File(file_path=TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH, controller=controller)
    return file


@pytest.fixture
def get_settings():
    return Settings(store=JsonStore)


@pytest.fixture
def get_app():
    class NotesApp(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = NotesModel(store=JsonStore, default_file=default_notes_file)
            self.controller = NotesController(
                settings=Settings(store=JsonStore), model=self.model
            )

    return NotesApp()
