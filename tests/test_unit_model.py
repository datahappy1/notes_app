import base64
import json
from os import getcwd

from dateutil.parser import parse

from notes_app.model.myscreen import MyScreenModel, FALLBACK_NOTES_FILE_PATH


class TestModel:
    def test_model(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        assert model
        assert model._file_path == f"{getcwd()}/assets/sample.txt"
        assert type(model._file_size) == int
        assert parse(model._last_updated_on)

        assert model.observers == []

        assert model.__repr__() == {'_file_path': f"{getcwd()}/assets/sample.txt",
                                    '_file_size': model.file_size,
                                    '_last_updated_on': f"{model.last_updated_on}"}

        assert model._get_attribute_to_formatted_name_map() == {'_file_path': 'File path',
                                                                '_file_size': 'File size (bytes)',
                                                                '_last_updated_on': 'Last updated on'}
        model.dump_encoded()

    def test_set_get_file_path(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        model.file_path = "test"
        assert model.file_path == "test"

    def test_set_get_file_size(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        model.file_size = 42
        assert model.file_size == 42

    def test_set_get_last_updated_on(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        model.last_updated_on = 1650621021
        assert model.last_updated_on == "2022-04-22 11:50:21"

    def test_formatted(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        # replace line break string "\r" with "" to achieve Win/Linux compatibility
        assert model.formatted == """File path : {cwd}/assets/sample.txt\r
File size (bytes) : {file_size}\r
Last updated on : {dt_now}"""\
            .replace("\r", "")\
            .format(cwd=getcwd(), file_size=model.file_size, dt_now=model.last_updated_on)

    def test_set_get_observers(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        observer = dict()
        model.add_observer(observer=observer)
        assert model.observers
        assert len(model.observers) == 1
        assert model.observers[0] == observer

    def test_dump_encoded(self):
        model = MyScreenModel(notes_file_path=FALLBACK_NOTES_FILE_PATH)
        assert model.dump_encoded() is None

    def test_safe_load(self):
        with open(file=f"{getcwd()}/model/myscreen.model", mode="rb") as test_file:
            test_file_data = test_file.read()
            assert test_file_data
            decoded_data = base64.decodebytes(test_file_data)
            assert type(test_file_data) == bytes

            json_data = json.loads(decoded_data)

            assert json_data["_file_path"] == f"{getcwd()}/assets/sample.txt"
            assert type(json_data["_file_size"]) == int
            assert parse(json_data["_last_updated_on"])
