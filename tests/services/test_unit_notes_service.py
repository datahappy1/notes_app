class TestNotesService:
    def test_transform_section_separator_to_section_name(self, get_notes_service):
        assert (
            get_notes_service.transform_section_separator_to_section_name(
                defaults=get_notes_service.defaults, section_separator="<section=a> "
            )
            == "a"
        )

    def test_transform_section_name_to_section_separator(self, get_notes_service):
        assert (
            get_notes_service.transform_section_name_to_section_separator(
                defaults=get_notes_service.defaults, section_name="a"
            )
            == "<section=a> "
        )
