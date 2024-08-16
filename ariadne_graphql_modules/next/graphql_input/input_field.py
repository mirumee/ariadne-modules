from typing import Any, Optional


class GraphQLInputField:
    name: Optional[str]
    description: Optional[str]
    graphql_type: Optional[Any]
    default_value: Optional[Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        graphql_type: Optional[Any] = None,
        default_value: Optional[Any] = None,
    ):
        self.name = name
        self.description = description
        self.graphql_type = graphql_type
        self.default_value = default_value
