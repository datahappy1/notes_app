import re
from typing import AnyStr, List, Dict

SECTION_FILE_SEPARATOR = "<section={name}>"
SECTION_FILE_SEPARATOR_DEFAULT_VALUE = "<section=default>"
SECTION_FILE_SEPARATOR_REGEX = "<section=[a-zA-Z]+>"
SECTION_FILE_NEW_SECTION_PLACEHOLDER = ""
SECTION_FILE_NAME_MINIMAL_CHAR_COUNT = 2


class File:
    def __init__(self, file_path, controller):
        self._file_path = file_path
        self._controller = controller
        self._raw_data_content: AnyStr = File._get_validated_raw_data(
            raw_data=self.get_raw_data_content()
        )
        self._sections: List[AnyStr] = self._get_sections_from_raw_data_content()
        self._data_by_sections: Dict[AnyStr, AnyStr] = \
            self._transform_raw_data_content_to_data_by_sections()

    @staticmethod
    def _get_validated_raw_data(raw_data):
        matches = re.findall(SECTION_FILE_SEPARATOR_REGEX, raw_data)
        if not matches:
            raise ValueError("No section in file found")
        return raw_data

    def get_raw_data_content(self):
        return self._controller.read_file_data(file_path=self._file_path)

    def _get_sections_from_raw_data_content(self):
        return re.findall(SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content)

    @property
    def default_section(self):
        return self._sections[0]

    @property
    def sections(self):
        return self._sections

    def add_section(self, section_name):
        self._sections.append(section_name)

    def delete_all_sections(self):
        self._sections = []

    def delete_section(self, section_name):
        self._sections.remove(section_name)

    def set_section_content(self, section_name, section_content):
        self._data_by_sections[section_name] = section_content

    def get_section_content(self, section_name):
        return self._data_by_sections[section_name]

    def delete_all_sections_content(self):
        self._data_by_sections = dict()

    def delete_section_content(self, section_name):
        self._data_by_sections.pop(section_name)

    def _transform_raw_data_content_to_data_by_sections(self):
        dict_data = dict()
        for item in zip(
                self._sections,
                re.split(SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content)[1:]
        ):
            dict_data[item[0]] = item[1]

        return dict_data

    def transform_data_by_sections_to_raw_data_content(self):
        text_data = str()
        for k, v in self._data_by_sections.items():
            text_data += k
            text_data += v

        return text_data
