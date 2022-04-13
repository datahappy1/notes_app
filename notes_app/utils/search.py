import re

DEFAULT_VALUE_SEARCH_CASE_SENSITIVE = False
DEFAULT_VALUE_SEARCH_ALL_SECTIONS = False
DEFAULT_VALUE_SEARCH_FULL_WORDS = False


class Search:
    def __init__(self):
        self._search_case_sensitive = DEFAULT_VALUE_SEARCH_CASE_SENSITIVE
        self._search_all_sections = DEFAULT_VALUE_SEARCH_ALL_SECTIONS
        self._search_full_words = DEFAULT_VALUE_SEARCH_FULL_WORDS

    @property
    def search_case_sensitive(self):
        return self._search_case_sensitive

    @search_case_sensitive.setter
    def search_case_sensitive(self, search_case_sensitive):
        self._search_case_sensitive = search_case_sensitive

    @property
    def search_all_sections(self):
        return self._search_all_sections

    @search_all_sections.setter
    def search_all_sections(self, search_all_sections):
        self._search_all_sections = search_all_sections

    @property
    def search_full_words(self):
        return self._search_full_words

    @search_full_words.setter
    def search_full_words(self, search_full_words):
        self._search_full_words = search_full_words

    @staticmethod
    def _search(pattern, text):
        return [m.start() for m in re.finditer(pattern, text)]

    @staticmethod
    def _case_sensitive_search(pattern, text):
        return Search._search(pattern=pattern, text=text)

    @staticmethod
    def _case_insensitive_search(pattern, text):
        pattern_lowered = pattern.lower()
        text_lowered = text.lower()
        return Search._search(pattern=pattern_lowered, text=text_lowered)

    def search_for_occurrences(self, pattern, file, current_section_name):
        found_occurrences = dict()

        # THE HOW'S TO SEARCH
        if self.search_case_sensitive:
            search_function = Search._case_sensitive_search
        else:
            search_function = Search._case_insensitive_search

        # THE WHAT'S TO SEARCH FOR
        if self.search_full_words:
            pattern = f" {pattern} "
        else:
            pass

        # THE WHERE'S TO SEARCH
        if self.search_all_sections:
            for section_name in file.sections:
                section_text = file.get_section_content(section_name=section_name)
                search_result = search_function(pattern=pattern, text=section_text)
                if search_result:
                    found_occurrences[section_name] = search_result
        else:
            text = file.get_section_content(section_name=current_section_name)
            search_result = search_function(pattern=pattern, text=text)
            if search_result:
                found_occurrences[current_section_name] = search_result

        return found_occurrences
