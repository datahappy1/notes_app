from typing import List

AVAILABLE_FONTS = [
    "DejaVuSans",
    "Roboto-Bold",
    "Roboto-BoldItalic",
    "Roboto-Italic",
    "Roboto-Regular",
    "RobotoMono-Regular",
]


def get_next_font(fonts_list: List[str], font_name: str) -> str:
    iterable_available_fonts = iter(fonts_list)

    for font in iterable_available_fonts:
        if font == font_name:
            return next(iterable_available_fonts, next(iter(fonts_list)))
