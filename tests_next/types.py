from enum import Enum

from ariadne_graphql_modules.next import GraphQLScalar


class ForwardScalar(GraphQLScalar):
    __schema__ = "scalar Forward"


class ForwardEnum(Enum):
    RED = "RED"
    BLU = "BLU"
