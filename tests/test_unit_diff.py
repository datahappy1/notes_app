import pytest

from notes_app.diff import _merge, _replace_line_endings, merge_strings


class TestDiff:
    @pytest.mark.parametrize(
        "left, right, result",
        [
            (
                "is",
                "this is some section.yeah",
                [["this"], ["is"], ["some", "section.yeah"]],
            ),
            (
                "is",
                "this some section.yeah",
                [["is"], ["this", "some", "section.yeah"]],
            ),
            ("", "this is some section.yeah", [["this", "is", "some", "section.yeah"]]),
            (
                "<section=first>",
                "<section=second>this is some section.yeah",
                [
                    ["<section=first>"],
                    ["<section=second>this", "is", "some", "section.yeah"],
                ],
            ),
            (
                "<section=first> some section text",
                "this is some section.yeah",
                [
                    ["<section=first>"],
                    ["this", "is"],
                    ["some"],
                    ["section", "text"],
                    ["section.yeah"],
                ],
            ),
            (
                "<section=first> some section text",
                "<section=first> another text <section=second>this is some section.yeah",
                [
                    ["<section=first>"],
                    ["another", "text", "<section=second>this", "is"],
                    ["some"],
                    ["section", "text"],
                    ["section.yeah"],
                ],
            ),
        ],
    )
    def test__merge(self, left, right, result):
        assert [x for x in _merge(left.split(), right.split())] == result

    def test__replace_line_endings(self):
        assert (
            _replace_line_endings(
                input_text="ad \n na", line_ending="\n", line_ending_replacement="!@#"
            )
            == "ad !@# na"
        )
        assert (
            _replace_line_endings(
                input_text="ad na", line_ending="\n", line_ending_replacement="!@#"
            )
            == "ad na"
        )

    @pytest.mark.parametrize(
        "before, after, result",
        [
            ("is", "this is some section.yeah", "this is some section.yeah"),
            ("is", "this some section.yeah", "is this some section.yeah"),
            ("", "this is some section.yeah", "this is some section.yeah"),
            (
                "<section=first>",
                "<section=second>this is some section.yeah",
                "<section=first> <section=second>this is some section.yeah",
            ),
            (
                "<section=first> some section text",
                "this is some section.yeah",
                "<section=first> this is some section text section.yeah",
            ),
            (
                "<section=first> some section text",
                "<section=first> another text <section=second>this is some section.yeah",
                "<section=first> another text <section=second>this is some section text section.yeah",
            ),
            (
                "<section=first> some \n section text",
                "this is some section.yeah",
                """<section=first> this is some 
 section text section.yeah""",
            ),
        ],
    )
    def test_merge_strings(self, before, after, result):
        assert merge_strings(before, after) == result
