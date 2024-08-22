from ariadne_graphql_modules import get_description_node


def test_no_description_is_returned_for_none():
    description = get_description_node(None)
    assert description is None


def test_no_description_is_returned_for_empty_str():
    description = get_description_node("")
    assert description is None


def test_description_is_returned_for_str():
    description = get_description_node("Example string.")
    assert description.value == "Example string."
    assert description.block is False


def test_description_is_stripped_for_whitespace():
    description = get_description_node("  Example string.\n")
    assert description.value == "Example string."
    assert description.block is False


def test_block_description_is_returned_for_multiline_str():
    description = get_description_node("Example string.\nNext line.")
    assert description.value == "Example string.\nNext line."
    assert description.block is True


def test_block_description_is_dedented():
    description = get_description_node("  Example string.\n  Next line.")
    assert description.value == "Example string.\nNext line."
    assert description.block is True
