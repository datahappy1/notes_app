from typing import List


class Color:
    def __init__(self, name, rgba_value):
        self.name = name
        self.rgba_value = rgba_value


# https://qconv.com/en/color_names-rgba
AVAILABLE_COLORS = [
    Color("black", (0, 0, 0, 1)),
    Color("navy", (0, 0, 0.5, 1)),
    Color("blue", (0, 0, 1, 1)),
    Color("green", (0, 0.5, 0, 1)),
    Color("teal", (0, 0.5, 0.5, 1)),
    Color("lime", (0, 1, 0, 1)),
    Color("aqua", (0, 1, 1, 1)),
    Color("maroon", (0.5, 0, 0, 1)),
    Color("purple", (0.5, 0, 0.5, 1)),
    Color("olive", (0.5, 0.5, 0, 1)),
    Color("gray", (0.5, 0.5, 0.5, 1)),
    Color("silver", (0.75, 0.75, 0.75, 1)),
    Color("red", (1, 0, 0, 1)),
    Color("fuchsia", (1, 0, 1, 1)),
    Color("yellow", (1, 1, 0, 1)),
    Color("white", (1, 1, 1, 1)),
]

AVAILABLE_SNACK_BAR_COLORS = [
    Color("success_green", (0.3, 0.5, 0.3, 0.9)),
    Color("failure_red", (0.9, 0.3, 0.3, 0.9)),
]


def get_color_by_name(colors_list: List[Color], color_name: str) -> Color:
    for color in colors_list:
        if color.name == color_name:
            return color


def get_next_color_by_rgba(
    colors_list: List[Color], rgba_value: List[int], skip_rgba_value: List[int] = None
) -> Color:
    iterable_available_colors = iter(colors_list)

    for color in iterable_available_colors:
        if color.rgba_value == tuple(rgba_value):
            next_color = next(iterable_available_colors, next(iter(colors_list)))

            if skip_rgba_value and next_color.rgba_value == tuple(skip_rgba_value):
                return get_next_color_by_rgba(
                    colors_list=colors_list,
                    rgba_value=next_color.rgba_value,
                    skip_rgba_value=skip_rgba_value,
                )

            return next_color
