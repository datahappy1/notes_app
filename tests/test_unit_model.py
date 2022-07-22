import json
import tempfile
import time
from datetime import datetime
from os import remove

from notes_app.model.notes_model import (
    format_local_epoch,
    get_file_updated_timestamp_as_epoch,
    get_current_epoch,
)


def test_format_local_epoch():
    assert isinstance(
        datetime.strptime(
            format_local_epoch("%Y-%m-%d %H:%M:%S", 1650362948), "%Y-%m-%d %H:%M:%S"
        ),
        datetime,
    )


def test_get_current_epoch():
    assert isinstance(get_current_epoch(), int)
    assert datetime.fromtimestamp(get_current_epoch())


def test_get_file_updated_timestamp_as_epoch():
    tf = tempfile.NamedTemporaryFile()
    assert datetime.fromtimestamp(get_file_updated_timestamp_as_epoch(tf.name))


class TestModel:
    def test_model(self, get_model):
        assert get_model._file_path == get_model.defaults.DEFAULT_NOTES_FILE_NAME
        assert isinstance(get_model._file_size, int)
        assert isinstance(datetime.fromtimestamp(get_model._last_updated_on), datetime)

        assert get_model.observers == []

        assert isinstance(get_model.__repr__(), str)
        assert json.dumps(get_model.__repr__())

    def test__set_missing_store_defaults(self, get_model):
        get_model.store.put("_file_path", value=None)
        get_model.store.put("_file_size", value=0)
        get_model.store.put("_last_updated_on", value=0)

        get_model._set_missing_store_defaults()

        assert get_model.store["_file_path"] == {
            "value": f"{get_model.defaults.DEFAULT_NOTES_FILE_NAME}"
        }
        # file size differs between OS types
        assert isinstance(get_model.store["_file_size"]["value"], int)
        assert isinstance(
            datetime.fromtimestamp(get_model.store["_last_updated_on"]["value"]),
            datetime,
        )

    def test_set_get_file_path(self, get_model):
        get_model.file_path = "test"
        assert get_model.file_path == "test"

    def test_file_path_exists(self, get_model):
        assert get_model.file_path
        assert get_model.file_path_exists is True

        remove(get_model.file_path)
        assert get_model.file_path_exists is False

    def test_formatted(self, get_model):
        assert isinstance(get_model.formatted, str)
        assert len(get_model.formatted.splitlines()) == 3

    def test_external_update(self, get_model):
        assert get_model.external_update is True

        # now set model.last_updated_on to current epoch time
        get_model._last_updated_on = time.time()
        assert get_model.external_update is False

        # now set model.last_updated_on to 0
        get_model._last_updated_on = 0
        assert get_model.external_update is False

    def test_set_get_observers(self, get_model):
        observer = dict()
        get_model.add_observer(observer=observer)
        assert get_model.observers
        assert len(get_model.observers) == 1
        assert get_model.observers[0] == observer

    def test_update(self, get_model):
        get_model._file_size = 0
        get_model._last_updated_on = 0

        fs_before = get_model._file_size
        ts_before = get_model._last_updated_on

        get_model.update()

        assert get_model._file_size > fs_before
        assert get_model._last_updated_on > ts_before

    def test_dump(self, get_model):
        get_model.file_path = get_model.defaults.DEFAULT_NOTES_FILE_NAME
        get_model._file_size = 123
        get_model._last_updated_on = 1653554504

        assert get_model.dump() is None

        assert get_model.store["_file_path"] == {
            "value": get_model.defaults.DEFAULT_NOTES_FILE_NAME
        }
        assert get_model.store["_file_size"] == {"value": 123}
        assert get_model.store["_last_updated_on"] == {"value": 1653554504}
