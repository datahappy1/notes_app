import pytest

from notes_app.diff import (
    _merge,
    _replace_line_endings,
    _split,
    _join,
    merge_strings,
)


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
                "",
                "this is some section.yeah",
                [["this", "is", "some", "section.yeah"],],
            ),
            (
                "some section text",
                "this is some section.yeah",
                [["this", "is"], ["some"], ["section", "text"], ["section.yeah"],],
            ),
            (
                "some section text",
                "another text",
                [["some", "section"], ["another"], ["text"],],
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
        "input_text, result",
        [
            (
                "this is some section.yeah",
                ["this", " ", "is", " ", "some", " ", "section", ".", "yeah"],
            ),
            ("another text", ["another", " ", "text"],),
        ],
    )
    def test__split(self, input_text, result):
        assert _split(input_text) == result

    @pytest.mark.parametrize(
        "input_list, result",
        [
            (["this", "is", "some", "section.yeah"], "this is some section.yeah",),
            (["another", "text"], "another text",),
        ],
    )
    def test__join(self, input_list, result):
        assert _join(input_list, separator=" ") == result

    @pytest.mark.parametrize(
        "before, after, result",
        [
            ("is", "this is some section.yeah", "this is some section.yeah"),
            ("is", "this some section.yeah", "is this some section.yeah"),
            ("", "this is some section.yeah", "this is some section.yeah"),
            ("", "this is some section.yeah", "this is some section.yeah",),
            (
                "some section text",
                "this is some section.yeah",
                "this is some section text.yeah",
            ),
            (
                "some section text",
                "another text this is some section.yeah",
                "another text this is some section text.yeah",
            ),
            (
                "some \n section text",
                "this is some section.yeah",
                """this is some 
 section text.yeah""",
            ),
        ],
    )
    def test_merge_strings(self, before, after, result):
        assert merge_strings(before, after) == result
