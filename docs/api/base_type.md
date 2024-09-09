
# `GraphQLType` Class Documentation

The `GraphQLType` class is a foundational class in the `ariadne_graphql_modules` library. It provides the absolute minimum structure needed to create a custom GraphQL type. This class is designed to be subclassed, allowing developers to define custom types with specific behaviors and properties in a GraphQL schema.

## Class Attributes

- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL type. If not provided, it will be generated based on the class name.
- **`__description__`**: *(Optional[str])* A description of the GraphQL type, included in the schema documentation.
- **`__abstract__`**: *(bool)* Indicates whether the class is abstract. Defaults to `True`.

## Core Methods

### `__get_graphql_name__(cls) -> str`

This method returns the GraphQL name of the type. If the `__graphql_name__` attribute is set, it returns that value. Otherwise, it generates a name based on the class name by removing common suffixes like "GraphQL", "Type", etc.

- **Returns:** `str` - The GraphQL name of the type.

### `__get_graphql_model__(cls, metadata: "GraphQLMetadata") -> "GraphQLModel"`

This method must be implemented by subclasses. It is responsible for generating the GraphQL model for the type. The model defines how the type is represented in a GraphQL schema.

- **Parameters:**
  - `metadata` (GraphQLMetadata): Metadata for the GraphQL model.
- **Returns:** `GraphQLModel` - The model representation of the type.

### `__get_graphql_types__(cls, _: "GraphQLMetadata") -> Iterable[Union[Type["GraphQLType"], Type[Enum]]]`

This method returns an iterable containing the GraphQL types associated with this type. By default, it returns the class itself.

- **Parameters:**
  - `_` (GraphQLMetadata): Metadata for the GraphQL model (unused in this method).
- **Returns:** `Iterable[Union[Type[GraphQLType], Type[Enum]]]` - The associated GraphQL types.

## Example Usage

### Creating a Custom GraphQL Type

To create a custom GraphQL type, subclass `GraphQLType` and implement the required methods.

```python
from ariadne_graphql_modules import GraphQLType, GraphQLMetadata, GraphQLModel

class MyCustomType(GraphQLType):
    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> GraphQLModel:
        # Implement the logic to create and return a GraphQLModel
        pass
```

### Custom Naming

You can specify a custom GraphQL name by setting the `__graphql_name__` attribute:

```python
class MyCustomType(GraphQLType):
    __graphql_name__ = "MyType"
    
    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> GraphQLModel:
        pass
```
