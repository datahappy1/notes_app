from typing import AnyStr, List

AVAILABLE_FONTS = [
    "DejaVuSans",
    "Roboto-Bold",
    "Roboto-BoldItalic",
    "Roboto-Italic",
    "Roboto-Regular",
    "RobotoMono-Regular",
]


def get_next_font(fonts_list: List[AnyStr], font_name: AnyStr) -> AnyStr:
    iterable_available_fonts = iter(fonts_list)

    for font in iterable_available_fonts:
        if font == font_name:
            return next(iterable_available_fonts, next(iter(AVAILABLE_FONTS)))
