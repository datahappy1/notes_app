SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_COLOR = "ff0000"
SEARCH_LIST_ITEM_MATCHED_HIGHLIGHT_STYLE = "b"


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
