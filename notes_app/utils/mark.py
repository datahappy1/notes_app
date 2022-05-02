import re

SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR = "ff0000"
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE = "b"

SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_COLOR = "ffaa00"
SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_STYLE = "i"


def _get_marked(input, highlight_style, highlight_color):
    return (
        f"[{highlight_style}]"
        f"[color={highlight_color}]"
        f"{input}"
        f"[/color]"
        f"[/{highlight_style}]"
    )


def get_marked_search_result(found_string):
    return _get_marked(
        input=found_string,
        highlight_style=SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE,
        highlight_color=SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR
    )


def get_marked_selected_text_input(selected_string):
    return _get_marked(
        input=selected_string,
        highlight_style=SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_STYLE,
        highlight_color=SELECTED_TEXT_INPUT_MATCHED_HIGHLIGHT_COLOR
    )


def is_selected_text_input_marked(selected_string, text):
    input_str = "adafa abc [color=red] hua def [/color] xyz"
    pattern = "def"

    COLOR_MARK_START = "\[color=[a-zA-Z]+]"
    COLOR_MARK_END = "\[/color]"

    pattern_location_index = input_str.index(pattern)

    # left_color_mark_starts = re.finditer(COLOR_MARK_START, input_str[0:pattern_location_index])
    left_color_mark_ends = re.finditer(COLOR_MARK_END, input_str[0:pattern_location_index])

    right_color_mark_starts = re.finditer(COLOR_MARK_START, input_str[pattern_location_index:])
    # right_color_mark_ends = re.finditer(COLOR_MARK_END, input_str[pattern_location_index:])

    # print([x for x in left_color_mark_starts])
    # print([x for x in left_color_mark_ends])
    #
    # print([x for x in right_color_mark_starts])
    # print([x for x in right_color_mark_ends])

    if left_color_mark_ends or right_color_mark_starts:
        return False
    return True
