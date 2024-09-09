from enum import Enum

from graphql import (
    DefinitionNode,
    FieldDefinitionNode,
    InputValueDefinitionNode,
)

FieldsDict = dict[str, FieldDefinitionNode]
InputFieldsDict = dict[str, InputValueDefinitionNode]
RequirementsDict = dict[str, type[DefinitionNode]]


class GraphQLClassType(Enum):
    BASE = "Base"
    OBJECT = "Object"
    INTERFACE = "Interface"
    SUBSCRIPTION = "Subscription"
