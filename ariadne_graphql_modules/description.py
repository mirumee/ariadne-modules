from textwrap import dedent
from typing import Optional

from graphql import StringValueNode


def get_description_node(description: Optional[str]) -> Optional[StringValueNode]:
    if not description:
        return None

    return StringValueNode(
        value=dedent(description).strip(), block="\n" in description.strip()
    )
