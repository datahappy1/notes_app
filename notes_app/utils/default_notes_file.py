from notes_app.utils.file import SECTION_FILE_SEPARATOR

DEFAULT_NOTES_FILE_NAME = "my_first_file.txt"
DEFAULT_NOTES_FILE_CONTENT = f"{SECTION_FILE_SEPARATOR.format(name='first')} Your first section. Here you can write your notes."


class DefaultNotesFile:
    def __init__(self, notes_file_name=None, notes_file_content=None):
        self.default_notes_file_name = notes_file_name or DEFAULT_NOTES_FILE_NAME
        self.default_notes_file_content = (
            notes_file_content or DEFAULT_NOTES_FILE_CONTENT
        )

    def generate_default_file(self) -> None:
        with open(file=self.default_notes_file_name, mode="w") as f:
            f.write(self.default_notes_file_content)
