import difflib
from typing import AnyStr

TEXT_FILE_LINE_BREAK_CHAR = "\n"
# TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT is used because difflib SequenceMatcher consumes line endings
# so we replace line endings with this temporary replacement and after retrieving the matched results we replace
# back text file line ending defined in TEXT_FILE_LINE_BREAK_CHAR
TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT = "Y3j28cXxSDaoSStrtLsj"


def _merge(left, right):
    """
    _merge
    https://stackoverflow.com/questions/37263682/how-to-find-union-of-two-strings-and-maintain-the-order
    """
    m = difflib.SequenceMatcher(None, left, right)
    for o, i1, i2, j1, j2 in m.get_opcodes():
        if o == "equal":
            yield left[i1:i2]
        elif o == "delete":
            yield left[i1:i2]
        elif o == "insert":
            yield right[j1:j2]
        elif o == "replace":
            yield left[i1:i2]
            yield right[j1:j2]


def _replace_line_endings(
    input_text: AnyStr, line_ending: AnyStr, line_ending_replacement: AnyStr
) -> AnyStr:
    """
    _replace_line_endings
    """
    return input_text.replace(line_ending, line_ending_replacement)


def merge_strings(before: AnyStr, after: AnyStr) -> AnyStr:
    """
    merge_strings
    """
    merged = _merge(
        _replace_line_endings(
            input_text=before,
            line_ending=TEXT_FILE_LINE_BREAK_CHAR,
            line_ending_replacement=TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT,
        ).split(),
        _replace_line_endings(
            input_text=after,
            line_ending=TEXT_FILE_LINE_BREAK_CHAR,
            line_ending_replacement=TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT,
        ).split(),
    )

    merged_result_list = [el for sublist in merged for el in sublist]

    return _replace_line_endings(
        input_text=" ".join(merged_result_list),
        line_ending=TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT,
        line_ending_replacement=TEXT_FILE_LINE_BREAK_CHAR,
    )
