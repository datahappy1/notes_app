import json
from os import getcwd
from os.path import exists

from dateutil.parser import parse

from notes_app.model.notes_model import DefaultNotesFile, DEFAULT_NOTES_FILE_NAME, DEFAULT_NOTES_FILE_CONTENT
from tests.conftest import read_model_file, TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH, \
    TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME, read_default_notes_file, delete_default_notes_file, \
    TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT


class TestDefaultNotesFile:
    def teardown_method(self, test_method):
        delete_default_notes_file()

    def test_default_notes_file(self):
        default_notes_file = DefaultNotesFile()
        assert default_notes_file.default_notes_file_name == DEFAULT_NOTES_FILE_NAME
        assert default_notes_file.default_notes_file_content == DEFAULT_NOTES_FILE_CONTENT

    def test_generate_default_file(self):
        DefaultNotesFile(
            notes_file_name=TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME,
            notes_file_content=TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT,
        ).generate()
        assert read_default_notes_file() == TEST_OVERRIDE_DEFAULT_NOTES_FILE_CONTENT


class TestModel:
    def test_model(self, get_model):
        assert get_model._file_path == TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH
        assert isinstance(get_model._file_size, int)
        assert parse(get_model._last_updated_on)

        assert get_model.observers == []

        assert get_model.__repr__() == json.dumps(
            {
                "_file_path": TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH,
                "_file_size": get_model.file_size,
                "_last_updated_on": f"{get_model.last_updated_on}",
            }
        )

        assert get_model._get_attribute_to_formatted_name_map() == {
            "_file_path": "File",
            "_file_size": "File size (bytes)",
            "_last_updated_on": "Last updated on",
        }
        assert get_model.dump() is None

    def test__generate_default_file_if_file_path_missing_invalid_path(self, get_model):
        get_model.file_path = "invalid_test_path"
        get_model.dump()
        get_model._generate_default_file_if_file_path_missing()
        assert exists(f"{getcwd()}/{TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME}")

    def test__generate_default_file_if_file_path_missing_missing_path(self, get_model):
        get_model.file_path = None
        get_model.dump()
        get_model._generate_default_file_if_file_path_missing()
        assert exists(f"{getcwd()}/{TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME}")

    def test__set_missing_store_defaults(self, get_model):
        get_model.file_path = None
        get_model.file_size = None
        get_model.last_updated_on = None
        get_model.dump()
        get_model._generate_default_file_if_file_path_missing()

        get_model._set_missing_store_defaults()

        json_data = read_model_file()

        assert json_data["_file_path"] == {"value": f"{getcwd()}/{TEST_OVERRIDE_DEFAULT_NOTES_FILE_NAME}"}
        # file size differs between OS types
        assert isinstance(json_data["_file_size"]["value"], int)
        assert parse(json_data["_last_updated_on"]["value"])

    def test_set_get_file_path(self, get_model):
        get_model.file_path = "test"
        assert get_model.file_path == "test"

    def test_set_get_file_size(self, get_model):
        get_model.file_size = 42
        assert get_model.file_size == 42

    def test_set_get_last_updated_on(self, get_model):
        get_model.last_updated_on = 1650621021
        assert get_model.last_updated_on == "2022-04-22 11:50:21"

    def test_formatted(self, get_model):
        assert " ".join(
            get_model.formatted.splitlines()
        ) == """File : {fp} File size (bytes) : {file_size} Last updated on : {dt_now}""".format(
            fp=TEST_OVERRIDE_DEFAULT_NOTES_FILE_PATH,
            file_size=get_model.file_size,
            dt_now=get_model.last_updated_on,
        )

    def test_set_get_observers(self, get_model):
        observer = dict()
        get_model.add_observer(observer=observer)
        assert get_model.observers
        assert len(get_model.observers) == 1
        assert get_model.observers[0] == observer

    def test_dump(self, get_model):
        get_model.file_path = "test"
        get_model.file_size = 123
        get_model.last_updated_on = 1653554504
        assert get_model.dump() is None

        json_data = read_model_file()

        assert json_data["_file_path"] == {"value": "test"}
        assert json_data["_file_size"] == {"value": 123}
        assert json_data["_last_updated_on"] == {"value": "2022-05-26 10:41:44"}
