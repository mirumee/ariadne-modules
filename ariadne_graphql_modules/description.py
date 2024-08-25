from textwrap import dedent
from typing import Optional

from graphql import StringValueNode


def get_description_node(description: Optional[str]) -> Optional[StringValueNode]:
    """Convert a description string into a GraphQL StringValueNode.

    If the description is provided, it will be dedented, stripped of surrounding
    whitespace, and used to create a StringValueNode. If the description contains
    newline characters, the `block` attribute of the StringValueNode
    will be set to `True`.
    """
    if not description:
        return None

    return StringValueNode(
        value=dedent(description).strip(), block="\n" in description.strip()
    )
