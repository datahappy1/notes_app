import base64
import json
from os import getcwd

from dateutil.parser import parse

from notes_app.model.myscreen import MyScreenModel


class TestModel:
    def test_model(self):
        model = MyScreenModel()
        assert model
        assert model._file_path == f"{getcwd()}/assets/sample.txt"
        assert model._file_size == 88
        assert parse(model._last_updated_on)

        assert model.observers == []

        assert model.__repr__() == {'_file_path': f"{getcwd()}/assets/sample.txt",
                                    '_file_size': 88,
                                    '_last_updated_on': f"{model.last_updated_on}"}

        assert model._get_attribute_to_formatted_name_map() == {'_file_path': 'File path',
                                                                '_file_size': 'File size (bytes)',
                                                                '_last_updated_on': 'Last updated on'}
        model.dump_encoded()

    def test_set_get_file_path(self):
        model = MyScreenModel()
        model.file_path = "test"
        assert model.file_path == "test"

    def test_set_get_file_size(self):
        model = MyScreenModel()
        model.file_size = 42
        assert model.file_size == 42

    def test_set_get_last_updated_on(self):
        model = MyScreenModel()
        model.last_updated_on = 1650621021
        assert model.last_updated_on == "2022-04-22 11:50:21"

    def test_formatted(self):
        model = MyScreenModel()
        assert model.formatted == """File path : {cwd}/assets/sample.txt\r
File size (bytes) : 88\r
Last updated on : {dt_now}""".format(cwd=getcwd(), dt_now=model.last_updated_on)

    def test_set_get_observers(self):
        model = MyScreenModel()
        observer = dict()
        model.add_observer(observer=observer)
        assert model.observers
        assert len(model.observers) == 1
        assert model.observers[0] == observer

    def test_dump_encoded(self):
        model = MyScreenModel()
        assert model.dump_encoded() is None

    def test_safe_load(self):
        with open(file=f"{getcwd()}/model/myscreen.model", mode="rb") as test_file:
            test_file_data = test_file.read()
            assert test_file_data
            decoded_data = base64.decodebytes(test_file_data)
            assert type(test_file_data) == bytes

            json_data = json.loads(decoded_data)

            assert json_data["_file_path"] == f"{getcwd()}/assets/sample.txt"
            assert json_data["_file_size"] == 88
            assert parse(json_data["_last_updated_on"])
