from typing import Dict, Type

from enum import Enum
from graphql import (
    DefinitionNode,
    FieldDefinitionNode,
    InputValueDefinitionNode,
)

FieldsDict = Dict[str, FieldDefinitionNode]
InputFieldsDict = Dict[str, InputValueDefinitionNode]
RequirementsDict = Dict[str, Type[DefinitionNode]]


class GraphQLClassType(Enum):
    BASE = "Base"
    OBJECT = "Object"
    INTERFACE = "Interface"
    SUBSCRIPTION = "Subscription"
