import re
from typing import List, Dict, Optional

SECTION_FILE_NEW_SECTION_PLACEHOLDER = ""
SECTION_FILE_NAME_MINIMAL_CHAR_COUNT = 2


def get_validated_file_path(file_path: str) -> Optional[str]:
    try:
        with open(file=file_path, mode="r", encoding="utf8"):
            pass
    except (PermissionError, FileNotFoundError, IsADirectoryError):
        return
    return file_path


def transform_section_separator_to_section_name(
    defaults, section_separator: str
) -> str:
    return re.search(
        defaults.DEFAULT_SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX, section_separator,
    ).group(1)


def transform_section_name_to_section_separator(defaults, section_name: str) -> str:
    return defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(name=section_name)


class File:
    def __init__(self, file_path, controller, defaults):
        self._file_path = file_path
        self._controller = controller

        self.defaults = defaults

        self._raw_data_content: str = self._get_validated_raw_data(
            raw_data=self.get_raw_data_content()
        )

        self._data_by_sections: Dict[
            str, str
        ] = self._transform_raw_data_content_to_data_by_sections()

    def _get_validated_raw_data(self, raw_data) -> str:
        matches = re.findall(
            self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_REGEX, raw_data
        )
        if not matches:
            raise ValueError("No section in file found")
        return raw_data

    def reload(self):
        """
        reload data from file to variables
        """
        self._raw_data_content = self._get_validated_raw_data(
            raw_data=self.get_raw_data_content()
        )

        self._data_by_sections = self._transform_raw_data_content_to_data_by_sections()

    def get_raw_data_content(self) -> str:
        return self._controller.read_file_data(file_path=self._file_path)

    @property
    def default_section_separator(self) -> str:
        return [k for k in self._data_by_sections.keys()][0]

    @property
    def section_separators_sorted(self) -> List[str]:
        return sorted([k for k in self._data_by_sections.keys()])

    def set_section_content(self, section_separator: str, section_content: str) -> None:
        self._data_by_sections[section_separator] = section_content

    def get_section_content(self, section_separator: str) -> str:
        return self._data_by_sections[section_separator]

    def delete_all_sections_content(self) -> None:
        self._data_by_sections = dict()

    def delete_section_content(self, section_separator: str) -> None:
        self._data_by_sections.pop(section_separator)

    def rename_section(
        self, old_section_separator: str, new_section_separator: str
    ) -> None:
        self._data_by_sections[new_section_separator] = self._data_by_sections[
            old_section_separator
        ]
        del self._data_by_sections[old_section_separator]

    def _transform_raw_data_content_to_data_by_sections(self) -> Dict[str, str]:
        result = dict()
        positions = []

        matches = re.finditer(
            self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content
        )
        matches_list = list(matches)
        for idx, match in enumerate(matches_list):
            _match_span = match.span()
            if idx > 0:
                positions.append((positions[len(positions) - 1][1], _match_span[0]))
            positions.append(_match_span)
            if idx + 1 == len(list(matches_list)):
                positions.append((_match_span[1], len(self._raw_data_content)))

        last_set_key = None
        for idx, pos in enumerate(positions):
            if idx % 2 == 0:
                section_separator = self._raw_data_content[pos[0] : pos[1]]
                result[section_separator] = last_set_key
                last_set_key = section_separator
            else:
                result[last_set_key] = self._raw_data_content[pos[0] : pos[1]]

        return result

    def transform_data_by_sections_to_raw_data_content(self) -> str:
        text_data = str()
        for k, v in self._data_by_sections.items():
            text_data += k
            text_data += v

        return text_data
