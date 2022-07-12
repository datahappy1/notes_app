import difflib
from typing import List

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
    input_text: str, line_ending: str, line_ending_replacement: str
) -> str:
    """
    _replace_line_endings
    """
    return input_text.replace(line_ending, line_ending_replacement)


SEPARATORS = {
    " ",  # (blank space)
    "~",  # (tilde)
    "`",  # (grave accent)
    "!",  # (exclamation mark)
    "@",  # (at)
    "#",  # (pound)
    "$",  # (dollar sign)
    "%",  # (percent)
    "^",  # (carat)
    "&",  # (ampersand)
    "*",  # (asterisk)
    "(",  # (open parenthesis)
    ")",  # (close parenthesis)
    "_",  # (underscore)
    "-",  # (hyphen)
    "+",  # (plus sign)
    "=",  # (equals)
    "{",  # (open brace)
    "}",  # (close brace)
    "[",  # (open bracket)
    "]",  # (close bracket)
    "|",  # (pipe)
    "\\",  # (backslash)
    ":",  # (colon)
    ";",  # (semicolon)
    "<",  # (less than)
    ",",  # (comma)
    ">",  # (greater than)
    ".",  # (period)
    "?",  # (question mark)
    "/",  # (forward slash)
}


def _split(input_text: str) -> List:
    result = []
    offset = 0
    for idx, string in enumerate(input_text):
        if string in SEPARATORS:
            result.append(input_text[offset:idx])
            result.append(string)
            offset = idx + 1
        # the last word in the enumerated input text
        if idx + 1 == len(input_text):
            result.append(input_text[offset : idx + 1])
    return result


def _join(input_list: List, separator: str) -> str:
    result = str()
    for idx, el in enumerate(input_list):
        if (
            idx == 0
            or (el in SEPARATORS)
            or (idx > 1 and input_list[idx - 1] in SEPARATORS)
        ):
            result += el
        else:
            result += f"{separator}{el}"
    return result


def merge_strings(before: str, after: str) -> str:
    """
    merge_strings
    """
    default_separator = " "
    merged = _merge(
        _split(
            _replace_line_endings(
                input_text=before,
                line_ending=TEXT_FILE_LINE_BREAK_CHAR,
                line_ending_replacement=TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT,
            )
        ),
        _split(
            _replace_line_endings(
                input_text=after,
                line_ending=TEXT_FILE_LINE_BREAK_CHAR,
                line_ending_replacement=TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT,
            )
        ),
    )

    merged_result_list = [el for sublist in merged for el in sublist]

    return _replace_line_endings(
        input_text=_join(input_list=merged_result_list, separator=default_separator),
        line_ending=TEXT_FILE_LINE_BREAK_CHAR_TEMP_REPLACEMENT,
        line_ending_replacement=TEXT_FILE_LINE_BREAK_CHAR,
    )
