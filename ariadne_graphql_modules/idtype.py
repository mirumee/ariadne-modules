from typing import Any, Union


class GraphQLID:
    __slots__ = ("value",)

    value: str

    def __init__(self, value: Union[int, str]):
        self.value = str(value)

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, (str, int)):
            return self.value == str(value)
        if isinstance(value, GraphQLID):
            return self.value == value.value
        return False

    def __int__(self) -> int:
        return int(self.value)

    def __str__(self) -> str:
        return self.value
