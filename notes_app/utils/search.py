import re

from notes_app.utils.file import File


class Search:
    def __init__(self, search_case_sensitive, search_all_sections):
        self.search_case_sensitive = search_case_sensitive
        self.search_all_sections = search_all_sections

    def search_for_occurrences(self, pattern, file: File, section_name):
        if self.search_all_sections:
            text = file.transform_data_by_sections_to_raw_data_content()
        else:
            text = file.get_section_content(section_name=section_name)

        if self.search_case_sensitive:
            pass
        else:
            pattern = pattern.lower()
            text = text.lower()

        found_occurrences = [
            m.start() for m in re.finditer(pattern, text)
        ]

        return found_occurrences
