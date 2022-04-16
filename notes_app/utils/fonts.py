AVAILABLE_FONTS = [
    "DejaVuSans",
    "Roboto-Bold",
    "Roboto-BoldItalic",
    "Roboto-Italic",
    "Roboto-Regular",
    "RobotoMono-Regular"
]


def get_next_font(font_name):
    iterable_available_fonts = iter(AVAILABLE_FONTS)

    for font in iterable_available_fonts:
        if font == font_name:
            return next(
                iterable_available_fonts,
                next(iter(AVAILABLE_FONTS))
            )
