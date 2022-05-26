from notes_app.utils.file import SECTION_FILE_SEPARATOR

DEFAULT_NOTES_FILE_NAME = "my_first_file.txt"
DEFAULT_NOTES_FILE_CONTENT = f"{SECTION_FILE_SEPARATOR.format(name='first')} Your first section. Here you can write your notes."


def generate_default_file(file_name, file_content) -> None:
    with open(file=file_name, mode="w") as f:
        f.write(file_content)
