import json
import os
from os import getcwd

import pytest
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp

from notes_app.defaults import Defaults
from notes_app.controller.notes_controller import NotesController
from notes_app.model.notes_model import NotesModel
from notes_app.file import File
from notes_app.settings import Settings

TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME = "my_first_file.txt"
TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH = getcwd()
TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH = f"{TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH}/{TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME}"
TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT = """<section=first> Quod equidem non reprehendo
<section=second> Quis istum dolorem timet"""

EMPTY_FILE_NAME = "empty.txt"
EMPTY_FILE_PATH = f"{TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH}/{EMPTY_FILE_NAME}"
EMPTY_FILE_CONTENT = """"""

DUMP_FILES_PATH = f"{TEST_OVERRIDE_DEFAULT_NOTES_FILE_DIR_PATH}/"

defaults = Defaults()
defaults.DEFAULT_NOTES_FILE_NAME = TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH
defaults.DEFAULT_NOTES_FILE_CONTENT = TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT


def create_settings_file():
    with open(
        file=f"{getcwd()}/{defaults.DEFAULT_SETTINGS_STORE_FILE_NAME}", mode="w", encoding="utf8"
    ) as f:
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
    fp = f"{getcwd()}/{defaults.DEFAULT_SETTINGS_STORE_FILE_NAME}"
    if os.path.exists(fp):
        os.remove(fp)


def create_model_file():
    with open(
        file=f"{getcwd()}/{defaults.DEFAULT_MODEL_STORE_FILE_NAME}", mode="w", encoding="utf8"
    ) as f:
        f.write(
            json.dumps(
                {
                    "_file_path": {"value": defaults.DEFAULT_NOTES_FILE_NAME},
                    "_file_size": {"value": 0},
                    "_last_updated_on": {"value": 1650870356},
                }
            )
        )


def delete_model_file():
    fp = f"{getcwd()}/{defaults.DEFAULT_MODEL_STORE_FILE_NAME}"
    if os.path.exists(fp):
        os.remove(fp)


def create_default_notes_file():
    with open(file=defaults.DEFAULT_NOTES_FILE_NAME, mode="w", encoding="utf8") as notes_file:
        notes_file.write(defaults.DEFAULT_NOTES_FILE_CONTENT)


def delete_default_notes_file():
    if os.path.exists(defaults.DEFAULT_NOTES_FILE_NAME):
        os.remove(defaults.DEFAULT_NOTES_FILE_NAME)


def create_default_notes_empty_file():
    with open(file=EMPTY_FILE_PATH, mode="w", encoding="utf8") as notes_file:
        notes_file.write(EMPTY_FILE_CONTENT)


def delete_default_notes_empty_file():
    if os.path.exists(EMPTY_FILE_PATH):
        os.remove(EMPTY_FILE_PATH)


def delete_dump_files():
    for file in os.listdir(DUMP_FILES_PATH):
        if file.startswith("__dump__"):
            os.remove(file)


@pytest.fixture(autouse=True)
def get_default_test_files_state():
    create_settings_file()
    create_model_file()
    create_default_notes_file()
    create_default_notes_empty_file()
    yield
    delete_settings_file()
    delete_model_file()
    delete_default_notes_file()
    delete_default_notes_empty_file()
    delete_dump_files()


@pytest.fixture
def get_empty_file_file_path():
    return EMPTY_FILE_PATH


@pytest.fixture
def get_model():
    return NotesModel(store=JsonStore, defaults=defaults)


@pytest.fixture()
def get_file():
    controller = NotesController(
        settings=Settings(store=JsonStore, defaults=defaults),
        model=NotesModel(store=JsonStore, defaults=defaults),
        defaults=defaults,
    )

    file = File(
        file_path=defaults.DEFAULT_NOTES_FILE_NAME,
        controller=controller,
        defaults=defaults,
    )
    return file


@pytest.fixture(autouse=True)
def get_settings():
    return Settings(store=JsonStore, defaults=defaults)


@pytest.fixture(autouse=True)
def get_app():
    class NotesApp(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.model = NotesModel(store=JsonStore, defaults=defaults)
            self.controller = NotesController(
                settings=Settings(store=JsonStore, defaults=defaults),
                model=self.model,
                defaults=defaults,
            )

    return NotesApp()
