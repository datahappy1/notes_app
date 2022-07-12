def get_marked_text(text: str, highlight_style: str, highlight_color: str) -> str:
    return (
        f"[{highlight_style}]"
        f"[color={highlight_color}]"
        f"{text}"
        f"[/color]"
        f"[/{highlight_style}]"
    )
