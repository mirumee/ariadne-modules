from typing import List, Type

from .bases import BaseType


class CollectionType(BaseType):
    __abstract__: bool = True
    __types__: List[Type[BaseType]] = []

    @classmethod
    def __get_types__(cls) -> List[Type["BaseType"]]:
        types: List[Type["BaseType"]] = []
        for type_ in cls.__types__:
            child_types = type_.__get_types__()
            for child_type in child_types:
                if child_type not in types:
                    types.append(child_type)
        return types
