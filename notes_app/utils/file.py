import re
from typing import AnyStr, List, Dict

SECTION_FILE_SEPARATOR = "<section={name}> "
SECTION_FILE_SEPARATOR_DEFAULT_VALUE = "<section=default> "
SECTION_FILE_SEPARATOR_REGEX = "<section=[a-zA-Z]+> "
SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX = "<section=(.+?)> "
SECTION_FILE_NEW_SECTION_PLACEHOLDER = ""
SECTION_FILE_NAME_MINIMAL_CHAR_COUNT = 2


class SectionIdentifier:
    def __init__(
        self, section_file_separator: AnyStr = None, section_name: AnyStr = None,
    ):
        if not section_file_separator and not section_name:
            raise ValueError(
                "Expected either section_file_separator or section_name args"
            )

        self.section_file_separator = (
            section_file_separator
            or self._transform_name_to_separator(section_name=section_name)
        )
        self.section_name = section_name or self._transform_separator_to_name()

    def _transform_separator_to_name(self) -> AnyStr:
        return re.search(
            SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX, self.section_file_separator
        ).group(1)

    def _transform_name_to_separator(self, section_name) -> AnyStr:
        return SECTION_FILE_SEPARATOR.format(name=section_name)


class File:
    def __init__(self, file_path, controller):
        self._file_path = file_path
        self._controller = controller

        self._raw_data_content: AnyStr = self._get_validated_raw_data(
            raw_data=self.get_raw_data_content()
        )

        self._section_identifiers: List[
            SectionIdentifier
        ] = self._get_section_identifiers_from_raw_data_content()

        self._data_by_sections: Dict[
            SectionIdentifier, AnyStr
        ] = self._transform_raw_data_content_to_data_by_sections()

    def _get_validated_raw_data(self, raw_data) -> AnyStr:
        matches = re.findall(SECTION_FILE_SEPARATOR_REGEX, raw_data)
        if not matches:
            raise ValueError("No section in file found")
        return raw_data

    def get_raw_data_content(self) -> AnyStr:
        return self._controller.read_file_data(file_path=self._file_path)

    def _get_section_identifiers_from_raw_data_content(self) -> List[SectionIdentifier]:
        separators = re.findall(SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content)
        return [SectionIdentifier(separator) for separator in separators]

    @property
    def default_section_identifier(self) -> SectionIdentifier:
        return self._section_identifiers[0]

    @property
    def section_identifiers(self) -> List[SectionIdentifier]:
        return self._section_identifiers

    def add_section_identifier(self, section_file_separator) -> None:
        self._section_identifiers.append(SectionIdentifier(section_file_separator))

    def delete_all_section_identifiers(self) -> None:
        self._section_identifiers = []

    def delete_section_identifier(self, section_file_separator) -> None:
        for section in self._section_identifiers:
            if section.section_file_separator == section_file_separator:
                self._section_identifiers.remove(section)

    def set_section_content(self, section_file_separator, section_content) -> None:
        self._data_by_sections[section_file_separator] = section_content

    def get_section_content(self, section_file_separator) -> AnyStr:
        return self._data_by_sections[section_file_separator]

    def delete_all_sections_content(self) -> None:
        self._data_by_sections = dict()

    def delete_section_content(self, section_file_separator) -> None:
        self._data_by_sections.pop(section_file_separator)

    def _transform_raw_data_content_to_data_by_sections(
        self,
    ) -> Dict[SectionIdentifier, AnyStr]:
        dict_data = dict()
        for item in zip(
            self._section_identifiers,
            re.split(SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content)[1:],
        ):
            dict_data[item[0].section_file_separator] = item[1]

        return dict_data

    def transform_data_by_sections_to_raw_data_content(self) -> AnyStr:
        text_data = str()
        for k, v in self._data_by_sections.items():
            text_data += k
            text_data += v

        return text_data
