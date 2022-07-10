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
        self.section_name = section_name or self._transform_separator_to_name()

    def _transform_separator_to_name(self) -> str:
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

        self._section_identifiers: List[
            SectionIdentifier
        ] = self._get_section_identifiers_from_raw_data_content()

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

        self._section_identifiers = (
            self._get_section_identifiers_from_raw_data_content()
        )
        self._data_by_sections = self._transform_raw_data_content_to_data_by_sections()

    def get_raw_data_content(self) -> str:
        return self._controller.read_file_data(file_path=self._file_path)

    def _get_section_identifiers_from_raw_data_content(self) -> List[SectionIdentifier]:
        separators = re.findall(
            self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_REGEX, self._raw_data_content
        )
        return [
            SectionIdentifier(defaults=self.defaults, section_file_separator=separator)
            for separator in separators
        ]

    @property
    def default_section_identifier(self) -> SectionIdentifier:
        return self._section_identifiers[0]

    @property
    def section_identifiers_sorted_by_name(self) -> List[SectionIdentifier]:
        self._section_identifiers.sort(key=lambda x: x.section_name)
        return self._section_identifiers

    def add_section_identifier(self, section_file_separator) -> None:
        self._section_identifiers.append(
            SectionIdentifier(
                defaults=self.defaults, section_file_separator=section_file_separator
            )
        )

    def delete_all_section_identifiers(self) -> None:
        self._section_identifiers = []

    def delete_section_identifier(self, section_file_separator) -> None:
        for section in self._section_identifiers:
            if section.section_file_separator == section_file_separator:
                self._section_identifiers.remove(section)

    def set_section_content(self, section_file_separator, section_content) -> None:
        self._data_by_sections[section_file_separator] = section_content

    def get_section_content(self, section_file_separator) -> str:
        return self._data_by_sections[section_file_separator]

    def delete_all_sections_content(self) -> None:
        self._data_by_sections = dict()

    def delete_section_content(self, section_file_separator) -> None:
        self._data_by_sections.pop(section_file_separator)

    def rename_section(
        self, old_section_file_separator, new_section_file_separator
    ) -> None:
        """
        rename_section method abstracts all section renaming actions
        by replacing the section identifier in the _section_identifiers list
        and by replacing the key in the _data_by_sections dict
        """

        # need to preserve the order of the _section_identifiers list item
        # and the _data_by_sections dict items so that new items are placed at the end

        for idx, section_identifier in enumerate(self._section_identifiers):
            if section_identifier.section_file_separator == old_section_file_separator:
                self._section_identifiers.pop(idx)

        self._section_identifiers.append(
            SectionIdentifier(
                defaults=self.defaults,
                section_file_separator=new_section_file_separator,
            )
        )

        self._data_by_sections[new_section_file_separator] = self._data_by_sections[
            old_section_file_separator
        ]
        del self._data_by_sections[old_section_file_separator]

    def _transform_raw_data_content_to_data_by_sections(self) -> Dict[str, str]:
        dict_data = dict()
        for item in zip(
            self._section_identifiers,
            re.split(
                self.defaults.DEFAULT_SECTION_FILE_SEPARATOR_REGEX,
                self._raw_data_content,
            )[1:],
        ):
            dict_data[item[0].section_file_separator] = item[1]
        return dict_data

    def transform_data_by_sections_to_raw_data_content(self) -> str:
        text_data = str()
        for k, v in self._data_by_sections.items():
            text_data += k
            text_data += v

        return text_data
