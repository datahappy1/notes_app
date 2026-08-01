from notes_app.view.markdown_renderer import (
    CustomMDLabel,
    CustomMDCard,
    CodeBlock,
    MDSeparator,
)

class TestMarkdownRenderer:
    def test_transform_inline_elements(self, get_markdown_renderer):
        result = get_markdown_renderer._transform_inline_elements(
            "**bold** *italic* https://example.com"
        )

        assert "[b]bold[/b]" in result
        assert "[i]italic[/i]" in result
        assert "[ref=https://example.com]" in result

    def test_render_heading1(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("# Heading")

        assert len(widgets) == 1
        assert isinstance(widgets[0], CustomMDLabel)
        assert widgets[0].text == "Heading"
        assert widgets[0].font_style == "H3"

    def test_render_heading2(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("## Heading")

        assert isinstance(widgets[0], CustomMDLabel)
        assert widgets[0].text == "Heading"
        assert widgets[0].font_style == "H4"

    def test_render_bullet(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("- item")

        assert isinstance(widgets[0], CustomMDLabel)
        assert widgets[0].text == "• item"

    def test_render_quote(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("> quote")

        assert isinstance(widgets[0], CustomMDCard)
        assert len(widgets[0].children) == 1

    def test_render_separator(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("---")

        assert isinstance(widgets[0], MDSeparator)

    def test_render_empty_line(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("")

        assert isinstance(widgets[0], CustomMDLabel)
        assert widgets[0].text == ""

    def test_render_plain_text(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render("hello world")

        assert isinstance(widgets[0], CustomMDLabel)
        assert widgets[0].text == "hello world"

    def test_render_code_block(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render(
            "```python\n"
            "print('hello')\n"
            "```"
        )

        assert len(widgets) == 1
        assert isinstance(widgets[0], CodeBlock)
        assert widgets[0].children[0].text == "print('hello')"

    def test_render_multiple_lines(self, get_markdown_renderer):
        widgets = get_markdown_renderer.render(
            "# Title\n"
            "\n"
            "- item"
        )

        assert len(widgets) == 3

        assert widgets[0].text == "Title"
        assert widgets[1].text == ""
        assert widgets[2].text == "• item"
