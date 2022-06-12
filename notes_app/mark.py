from typing import AnyStr


def get_marked_text(
    text: AnyStr, highlight_style: AnyStr, highlight_color: AnyStr
) -> AnyStr:
    return (
        f"[{highlight_style}]"
        f"[color={highlight_color}]"
        f"{text}"
        f"[/color]"
        f"[/{highlight_style}]"
    )
