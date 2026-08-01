import re
import webbrowser
from typing import List

from kivymd.uix.card import MDSeparator, MDCard
from kivymd.uix.label import MDLabel

URL_REGEX = re.compile(
    r"(https?://\S+)"
)

_LINE_SEPARATOR = "\n"
_EMPTY_LINE_HEIGHT = "12dp"
_CARD_PADDING = "10dp"
_CARD_SPACING = "5dp"
_CARD_RADIUS = 8
_CODE_BLOCK_SEPARATOR = "```"
_CODE_BLOCK_FONT = "RobotoMono-Regular"



class CustomMDLabel(MDLabel):
    def __init__(self, **kwargs):
        super(CustomMDLabel, self).__init__(**kwargs)
        self.adaptive_height = True
        self.markup = True
        self.bind(on_ref_press=self._open_link)

    @staticmethod
    def _open_link(instance, url):
        webbrowser.open(url)

class CustomMDCard(MDCard):
    def __init__(self, **kwargs):
        super(CustomMDCard, self).__init__(**kwargs)
        self.adaptive_height = True
        self.padding=_CARD_PADDING

class CodeBlock(MDCard):
    def __init__(self, code: str, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = _CARD_PADDING
        self.spacing = _CARD_SPACING
        self.radius = [_CARD_RADIUS]

        self.add_widget(
            MDLabel(
                text=code,
                font_name=_CODE_BLOCK_FONT,
                adaptive_height=True,
            )
        )

def get_heading1(line: str) -> CustomMDLabel:
    return CustomMDLabel(
        text=line[2:],
        font_style="H3",
    )

def get_heading2(line: str) -> CustomMDLabel:
    return CustomMDLabel(
        text=line[3:],
        font_style="H4",
    )

def get_heading3(line: str) -> CustomMDLabel:
    return CustomMDLabel(
        text=line[4:],
        font_style="H5",
    )

def get_bullet(line: str) -> CustomMDLabel:
    return CustomMDLabel(
        text=f"• {line[2:]}",
    )

def get_indented_bullet(line: str) -> CustomMDLabel:
    return CustomMDLabel(
        text=f"    - {line[3:]}",
    )

def get_quote(line: str) -> CustomMDCard:
    card = CustomMDCard()

    card.add_widget(
        CustomMDLabel(
            text=line[2:],
        )
    )
    return card

def get_separator() -> MDSeparator:
    return MDSeparator()

def get_empty_label() -> CustomMDLabel:
    return CustomMDLabel(
        text="",
        height=_EMPTY_LINE_HEIGHT,
    )

def get_plain_label(line: str) -> CustomMDLabel:
    return CustomMDLabel(
        text=line,
    )

class MarkdownRenderer:
    @staticmethod
    def _transform_inline_elements(text: str) -> str:
        text = re.sub(r"\*\*(.+?)\*\*", r"[b]\1[/b]", text)
        text = re.sub(r"\*(.+?)\*", r"[i]\1[/i]", text)

        # URLs
        text = URL_REGEX.sub(r"[ref=\1][color=#2196F3][u]\1[/u][/color][/ref]",text)
        return text

    def _render_line(self, line: str) -> CustomMDLabel | MDSeparator | CustomMDCard:
        if not line.strip():
            return get_empty_label()

        handlers = (
            ("### ", get_heading3, line),
            ("## ", get_heading2, line),
            ("# ", get_heading1, line),
            ("- ", get_bullet, line),
            ("-- ", get_indented_bullet, line),
            ("> ", get_quote, line),
            ("---", get_separator, None),
        )

        for prefix, handler, param in handlers:
            if line.startswith(prefix):
                return handler(param) if param else handler()

        return get_plain_label(
            line=self._transform_inline_elements(line)
        )

    def render(self, text: str) -> List[CustomMDLabel | MDSeparator | CustomMDCard]:
        widgets = []

        inside_code = False
        code_buffer = []

        for line in text.split(_LINE_SEPARATOR):
            if inside_code:
                if line.startswith(_CODE_BLOCK_SEPARATOR):
                    widgets.append(
                        CodeBlock(
                            code="\n".join(code_buffer),
                        )
                    )

                    inside_code = False
                    code_buffer = []
                else:
                    code_buffer.append(line)
                continue

            if line.startswith(_CODE_BLOCK_SEPARATOR):
                inside_code = True
                continue

            rendered_line = self._render_line(line)
            widgets.append(rendered_line)

        return widgets
