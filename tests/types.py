from enum import Enum

from ariadne_graphql_modules import GraphQLScalar


class ForwardScalar(GraphQLScalar):
    __schema__ = "scalar Forward"


class ForwardEnum(Enum):
    RED = "RED"
    BLU = "BLU"
