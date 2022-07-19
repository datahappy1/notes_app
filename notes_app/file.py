import re
from typing import List, Dict

SECTION_FILE_NEW_SECTION_PLACEHOLDER = ""
SECTION_FILE_NAME_MINIMAL_CHAR_COUNT = 2


def get_validated_file_path(file_path):
    try:
        with open(file=file_path, mode="r"):
            pass
    except (PermissionError, FileNotFoundError, IsADirectoryError):
        return
    return file_path


class SectionIdentifier:
    def __init__(
        self, defaults, section_file_separator: str = None, section_name: str = None,
    ):
        self.defaults = defaults

        if not section_file_separator and not section_name:
            raise ValueError(
                "Expected either section_file_separator or section_name args"
            )

        self.section_file_separator = (
            section_file_separator
            or self._transform_name_to_separator(section_name=section_name)
        )
        print(">>>", section_file_separator, "<<<", section_name)
        self.section_name = section_name or self._transform_separator_to_name()

    def _transform_separator_to_name(self) -> str:
        print("___", self.section_file_separator, "-",self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX,":::")
        return re.search(
            self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_GROUP_SUBSTR_REGEX,
            self.section_file_separator,
        ).group(1)

    def _transform_name_to_separator(self, section_name) -> str:
        return self.defaults.DEFAULT_SECTION_FILE_SEPARATOR.format(name=section_name)


class File:
    def __init__(self, file_path, controller, defaults):
        self._file_path = file_path
        self._controller = controller

        self.defaults = defaults

        self._raw_data_content: str = self._get_validated_raw_data(
            raw_data=self.get_raw_data_content()
        )

        self._data_by_sections: Dict[
            SectionIdentifier, str
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
    def default_section_identifier(self) -> SectionIdentifier:
        return [k for k in self._data_by_sections.keys()][0]

    @property
    def section_identifiers_sorted_by_name(self) -> List[SectionIdentifier]:
        section_identifiers = [k for k in self._data_by_sections.keys()]
        section_identifiers.sort(key=lambda x: x.section_name)
        return section_identifiers

    def set_section_content(self, section_identifier, section_content) -> None:
        self._data_by_sections[section_identifier] = section_content

    def get_section_content(self, section_identifier) -> str:
        return self._data_by_sections[section_identifier]

    def delete_all_sections_content(self) -> None:
        self._data_by_sections = dict()

    def delete_section_content(self, section_identifier) -> None:
        self._data_by_sections.pop(section_identifier)

    def rename_section(
        self, old_section_file_separator, new_section_file_separator
    ) -> None:

        old_section_identifier = SectionIdentifier(
            section_file_separator=old_section_file_separator, defaults=self.defaults
        )
        new_section_identifier = SectionIdentifier(
            section_file_separator=new_section_file_separator, defaults=self.defaults
        )

        self._data_by_sections[new_section_identifier] = self._data_by_sections[
            old_section_identifier
        ]
        del self._data_by_sections[old_section_identifier]

    def _transform_raw_data_content_to_data_by_sections(self) -> Dict[SectionIdentifier, str]:
        dict_data = dict()

        result = []
        positions = []
        matches = re.finditer(self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content)
        matches_list = list(matches)
        for idx, match in enumerate(matches_list):
            match_span = match.span()
            if idx > 0:
                positions.append((positions[len(positions) - 1][1], match_span[0]))
            positions.append(match_span)
            if idx + 1 == len(list(matches_list)):
                positions.append((match_span[1], len(self._raw_data_content)))

        for pos in positions:
            result.append(self._raw_data_content[pos[0]:pos[1]])

        for idx,item in enumerate(result):
            if idx == 0:
                continue
            print("|||",result[idx-1],"|||")
            si = SectionIdentifier(section_file_separator=result[idx-1], defaults=self.defaults)
            dict_data[si]=item

        print("xxxd", dict_data)

        return dict_data

    def transform_data_by_sections_to_raw_data_content(self) -> str:
        text_data = str()
        for k, v in self._data_by_sections.items():
            text_data += k
            text_data += v

        return text_data
