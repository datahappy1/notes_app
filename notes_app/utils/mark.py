import re

SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR = "ff0000"
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE = "b"

SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_COLOR = "ffaa00"
SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_STYLE = "i"

COLOR_MARK_START = r"\[color=[a-zA-Z]+]"
COLOR_MARK_END = r"\[/color]"


def _get_marked(string, highlight_style, highlight_color):
    return (
        f"[{highlight_style}]"
        f"[color={highlight_color}]"
        f"{string}"
        f"[/color]"
        f"[/{highlight_style}]"
    )


def get_marked_search_result(found_string):
    return _get_marked(
        string=found_string,
        highlight_style=SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE,
        highlight_color=SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR,
    )


def get_marked_selected_text_input(selected_string):
    return _get_marked(
        string=selected_string,
        highlight_style=SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_STYLE,
        highlight_color=SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_COLOR,
    )


def is_selected_text_input_marked(cursor_index, text):
    l_side_color_mark_starts = [
        x for x in re.finditer(COLOR_MARK_START, text[0:cursor_index])
    ]
    l_side_color_mark_ends = [
        x for x in re.finditer(COLOR_MARK_END, text[0:cursor_index])
    ]

    r_side_color_mark_starts = [
        x for x in re.finditer(COLOR_MARK_START, text[cursor_index:])
    ]
    r_side_color_mark_ends = [
        x for x in re.finditer(COLOR_MARK_END, text[cursor_index:])
    ]

    if (
        l_side_color_mark_starts
        and r_side_color_mark_ends
        and not l_side_color_mark_ends
        and not r_side_color_mark_starts
    ):
        return True

    if len(l_side_color_mark_starts) > len(l_side_color_mark_ends):
        return True

    return False
