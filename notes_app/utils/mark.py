def get_marked_search_result(found_string, highlight_style, highlight_color):
    return (
        f"[{highlight_style}]"
        f"[color={highlight_color}]"
        f"{found_string}"
        f"[/color]"
        f"[/{highlight_style}]"
    )
