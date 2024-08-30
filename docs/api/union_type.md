# `GraphQLUnion`

The `GraphQLUnion` class is used to define custom union types in GraphQL. A union type is a GraphQL feature that allows a field to return one of several different types, but only one of them at any given time. This class provides the framework for defining unions, managing their types, and handling type resolution.

## Inheritance

- Inherits from `GraphQLType`.

## Class Attributes

- **`__types__`**: **Sequence[Type[GraphQLType]]** - A sequence of GraphQL types that belong to the union.
- **`__schema__`**: *(Optional[str])* - The GraphQL schema definition string for the union, if provided.

## Class Methods

### `resolve_type(obj: Any, *_) -> str`

Resolves the type of an object at runtime. It returns the name of the GraphQL type that matches the object's type.

- **Parameters:**
  - `obj` (Any): The object to resolve the type for.

- **Returns:** `str` - The name of the resolved GraphQL type.

## Example Usage

### Defining a Union Type

To define a union type, subclass `GraphQLUnion` and specify the types that belong to the union using the `__types__` attribute.

```python
from ariadne_graphql_modules import GraphQLUnion, GraphQLObject

class UserType(GraphQLObject):
    id: GraphQLID
    username: str

class CommentType(GraphQLObject):
    id: GraphQLID
    content: str

class ResultType(GraphQLUnion):
    __types__ = [UserType, CommentType]
```

### Using a Union Type in a Schema

You can use the defined union type in a GraphQL schema to handle fields that can return multiple types.

```python
from ariadne_graphql_modules import GraphQLObject, make_executable_schema

class QueryType(GraphQLObject):
    @GraphQLObject.field(graphql_type=List[ResultType])
    @staticmethod
    def search(*_) -> List[Union[UserType, CommentType]]:
        return [
            UserType(id=1, username="Bob"),
            CommentType(id=2, content="Hello World!"),
        ]

schema = make_executable_schema(QueryType)
```

### Handling Unions with and without Schema

You can define a union with or without an explicit schema definition:

```python
class SearchResultUnion(GraphQLUnion):
    __schema__ = "union SearchResult = User | Comment"
    __types__ = [UserType, CommentType]
```

### Validation

The `GraphQLUnion` class includes validation mechanisms to ensure that union types are correctly defined. The validation checks whether the types in `__types__` match those in `__schema__` if a schema is provided.

#### Validation Process

1. **Type List Validation**: Ensures that the `__types__` attribute is provided and contains valid types.
2. **Schema Parsing and Validation**: If `__schema__` is provided, it is parsed to ensure it corresponds to a valid GraphQL union type.
3. **Type Matching**: Validates that the types in `__types__` match the types declared in `__schema__`, if a schema is provided.

#### Validation Example

```python
from graphql import gql
from ariadne_graphql_modules import GraphQLUnion, GraphQLObject

class UserType(GraphQLObject):
    id: GraphQLID
    username: str

class CommentType(GraphQLObject):
    id: GraphQLID
    content: str

class ResultType(GraphQLUnion):
    __schema__ = gql("""
    union Result = User | Comment
    """)
    __types__ = [UserType, CommentType]
```

If the `__schema__` defines types that do not match those in `__types__`, a `ValueError` will be raised.
