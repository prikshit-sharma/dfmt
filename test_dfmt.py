import pytest

from dfmt import reformat, split_regions, get_prefix, process_multiline_comments, preserve_line_breaks


def test_get_prefix():
    assert get_prefix("# ") == "# "
    assert get_prefix(" * ") == " * "
    assert get_prefix(" > ") == " > "
    assert get_prefix(">> ") == ">> "


class TestRegions:
    @staticmethod
    def test_one_line():
        text = "hello"
        regions = split_regions(text)
        assert len(regions) == 1
        actual = regions[0]
        assert actual.prefix == ""
        assert actual.text == "hello\n"

    @staticmethod
    def test_two_lines():
        text = "hello\nworld"
        regions = split_regions(text)
        assert len(regions) == 1
        actual = regions[0]
        assert actual.prefix == ""
        assert actual.text == "hello\nworld\n"

    @staticmethod
    def test_one_indented_paragraph():
        text = """\
  hello
  world
"""
        regions = split_regions(text)
        assert len(regions) == 1
        actual = regions[0]
        assert actual.prefix == "  "
        assert actual.text == "  hello\n  world\n"

    @staticmethod
    def test_two_indented_paragraphs():
        text = """\
  hello
  world

  goodbye
  world
"""
        regions = split_regions(text)
        one, two, three = regions
        assert two.prefix == ""
        assert two.text == "\n"

    @staticmethod
    def test_two_paragraphs_in_pound_comment():
        text = """\
  # this is the
  # first paragraph
  #
  # this is the
  # second paragraph
"""
        regions = split_regions(text)
        one, two, three = regions
        assert two.prefix == "  "
        assert two.text == "  #\n"


def test_empty_selection():
    assert reformat("") == "\n"


def test_empty_line():
    assert reformat("\n") == "\n"


def test_blank_line():
    assert reformat("   \n") == "\n"


def test_keep_small_lines():
    assert reformat("this is small", width=20) == "this is small\n"


def test_keep_long_words():
    assert (
        reformat(
            "this is a very big url: https://a.very.long.domain.tld/a/very/long/path",
            width=40,
        )
        == "this is a very big url:\nhttps://a.very.long.domain.tld/a/very/long/path\n"
    )


def test_into_two_lines():
    assert reformat("aaa bbb", width=3) == "aaa\nbbb\n"


def test_into_three_lines():
    assert reformat("aaa bb ccc", width=3) == "aaa\nbb\nccc\n"


def test_long_sentence():
    assert (
        reformat("this is a pretty big sentence in two pretty big parts", width=12)
        == "this is a\npretty big\nsentence in\ntwo pretty\nbig parts\n"
    )


def test_pound_comment_1_to_2():
    assert (
        reformat("# this is a pretty big comment, isn't it?", width=20)
        == "# this is a pretty\n# big comment, isn't\n# it?\n"
    )


def test_pound_comment_2_to_3():
    text = """\
# aaa bbb
# ccc
"""
    expected = """\
# aaa
# bbb
# ccc
"""
    actual = reformat(text, width=5)
    if actual != expected:
        pytest.fail(actual)


def test_doxygen():
    text = """\
 * this is a pretty big line in a doxygen comment
"""
    expected = """\
 * this is a pretty
 * big line in a
 * doxygen comment
"""
    actual = reformat(text, width=20)
    if actual != expected:
        pytest.fail(actual)


def test_preserve_leading_indent():
    text = " aaa bbb"
    assert reformat(text, width=4) == " aaa\n bbb\n"


def test_indented_pound_comment():
    text = """\
    # this is a pretty big line in a Python comment that is indented
"""
    expected = """\
    # this is a pretty big line in a
    # Python comment that is indented
"""
    actual = reformat(text, width=40)
    if actual != expected:
        pytest.fail(actual)


def test_pound_paragraphs():
    text = """\
    # this is a pretty big line in a Python comment that is indented
    #
    # and this is a second big line in a Python comment that is indented
"""
    expected = """\
    # this is a pretty big line in a
    # Python comment that is indented
    #
    # and this is a second big line in a
    # Python comment that is indented
"""
    actual = reformat(text, width=40)
    if actual != expected:
        pytest.fail(actual)


def test_empty_line_between_regions():
    text = """\
# first line

# second line
"""
    expected = """\
# first line

# second line
"""
    actual = reformat(text, width=20)
    if actual != expected:
        pytest.fail(actual)


def test_quoting_simple():
    text = """\
> Inline comment by a third party which wraps onto multiple lines
"""
    expected = """\
> Inline comment by a third
> party which wraps onto
> multiple lines
"""
    actual = reformat(text, width=30)
    if actual != expected:
        pytest.fail(actual)


def test_quoting_nested():
    text = """\
> Inline commentary by a third party which also wraps onto multiple lines

> > Some kind of very long text that's being quoted by somebody else.
"""

    expected = """\
> Inline commentary by a third party which also
> wraps onto multiple lines

> > Some kind of very long text that's being
> > quoted by somebody else.
"""
    actual = reformat(text, width=50)
    if actual != expected:
        pytest.fail(actual)

# New testcase for multiline_comment
def test_process_multiline_comments():
    """
    This test ensures that the process_multiline_comments function 
    correctly preserves multiline comments in the input text.
    
    Input:
    - A string containing multiple multiline comments.
    
    Expected Output:
    - The multiline comments should remain unchanged after processing.
    """
    text = """\
\"\"\" 
This is a multiline comment.
It should be preserved.
\"\"\" 
print("Hello, World!")
\"\"\" 
Another comment.
\"\"\" 
"""
    expected = """\
\"\"\" 
This is a multiline comment.
It should be preserved.
\"\"\" 
print("Hello, World!")
\"\"\" 
Another comment.
\"\"\" 
"""
    actual = process_multiline_comments(text)
    
    # If the processed text does not match the expected output, fail the test
    if actual != expected:
        pytest.fail(f"Expected:\n{expected}\nActual:\n{actual}")


# New testcase for line breaks
def test_preserve_line_breaks():
    """
    This test checks that the preserve_line_breaks function 
    correctly retains line breaks in the input text.
    
    Input:
    - A string containing multiple lines, with blank lines in between.
    
    Expected Output:
    - Line breaks should be preserved with spaces added after each line break.
    """
    text = """\
Line 1.
Line 2.

Line 4 after a blank line.
"""
    expected = """\
Line 1. 
Line 2. 

Line 4 after a blank line. 
"""
    actual = preserve_line_breaks(text)
    
    # Assert that the actual output matches the expected output
    assert actual == expected, f"Expected:\n{expected}\nActual:\n{actual}"