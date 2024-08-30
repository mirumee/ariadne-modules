# `GraphQLInput`

`GraphQLInput` is a base class used to define GraphQL input types in a modular way. It allows you to create structured input objects with fields, default values, and custom validation, making it easier to handle complex input scenarios in your GraphQL API.

## Inheritance

- Inherits from `GraphQLType`.

## Class Attributes

- **`__schema__`**: *(Optional[str])* - The GraphQL schema definition string for the union, if provided.
- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL type. If not provided, it will be generated based on the class name.
- **`__description__`**: *(Optional[str])* A description of the GraphQL type, included in the schema documentation.
- **`__out_names__`**: *(Optional)* A dictionary to customize the names of fields when they are used as output in other parts of the schema.

## Class Methods

### `field`

A static method that defines a field within the input type. It allows you to specify the field's name, type, description, and default value.

```python
@staticmethod
def field(
    *,
    name: Optional[str] = None,
    graphql_type: Optional[Any] = None,
    description: Optional[str] = None,
    default_value: Optional[Any] = None,
) -> Any:
    ...
```

## Examples

### Basic Input Type

Here’s how to define a basic input type using `GraphQLInput`:

```python
from ariadne_graphql_modules import GraphQLInput

class SearchInput(GraphQLInput):
    query: str
    age: int
```

### Input Type with Default Values

You can define default values for input fields using class attributes:

```python
class SearchInput(GraphQLInput):
    query: str = "default search"
    age: int = 18
```

### Input Type with Custom Field Definitions

You can use the `field` method to define fields with more control over their attributes, such as setting a default value or adding a description:

```python
class SearchInput(GraphQLInput):
    query: str = GraphQLInput.field(default_value="default search", description="Search query")
    age: int = GraphQLInput.field(default_value=18, description="Age filter")
```

### Using `GraphQLInput` in a Query

The `GraphQLInput` can be used as an argument in GraphQL object types. This allows you to pass complex structured data to queries or mutations.

```python
from ariadne_graphql_modules import GraphQLInput, GraphQLObject, make_executable_schema


class SearchInput(GraphQLInput):
    query: Optional[str]
    age: Optional[int]

class QueryType(GraphQLObject):
    search: str

    @GraphQLObject.resolver("search")
    def resolve_search(*_, input: SearchInput) -> str:
        return f"{repr([input.query, input.age])}"
```

In this example, `SearchInput` is used as an argument in the `search` query, allowing clients to pass in a structured input object.

## Validation

Validation is a key feature of `GraphQLInput`. The class provides built-in validation to ensure that the input schema and fields are correctly defined and that they adhere to GraphQL standards.

### Validation Scenarios

#### 1. Invalid Schema Type

If the schema defined in `__schema__` does not correspond to an input type, a `ValueError` is raised.

```python
from ariadne import gql
from ariadne_graphql_modules import GraphQLInput

try:
    class CustomType(GraphQLInput):
        __schema__ = gql("scalar Custom")
except ValueError as e:
    print(e)  # Outputs error regarding invalid type schema
```

#### 2. Name Mismatch

If the class name and the name defined in the schema do not match, a `ValueError` is raised.

```python
try:
    class CustomType(GraphQLInput):
        __graphql_name__ = "Lorem"
        __schema__ = gql(
            '''
            input Custom {
                hello: String!
            }
            '''
        )
except ValueError as e:
    print(e)  # Outputs error regarding name mismatch
```

#### 3. Duplicate Descriptions

If both the class and the schema define a description, a `ValueError` is raised due to the conflict.

```python
try:
    class CustomType(GraphQLInput):
        __description__ = "Hello world!"
        __schema__ = gql(
            """
            Other description
            """
            input Custom {
              hello: String!
            }
            '''
        )
except ValueError as e:
    print(e)  # Outputs error regarding duplicate descriptions
```

#### 4. Missing Fields in Schema

If the input schema is missing fields, a `ValueError` is raised.

```python
try:
    class CustomType(GraphQLInput):
        __schema__ = gql("input Custom")
except ValueError as e:
    print(e)  # Outputs error regarding missing fields
```

#### 5. Invalid `__out_names__` without Schema

If `__out_names__` is defined without a schema, a `ValueError` is raised since this feature requires an explicit schema.

```python
try:
    class CustomType(GraphQLInput):
        hello: str

        __out_names__ = {
            "hello": "ok",
        }
except ValueError as e:
    print(e)  # Outputs error regarding unsupported out_names without schema
```

#### 6. Invalid or Duplicate Out Names

If an out name is defined for a non-existent field or if there are duplicate out names, a `ValueError` is raised.

```python
try:
    class CustomType(GraphQLInput):
        __schema__ = gql(
            '''
            input Query {
              hello: String!
            }
            '''
        )

        __out_names__ = {
            "invalid": "ok",  # Invalid field name
        }
except ValueError as e:
    print(e)  # Outputs error regarding invalid out_name

try:
    class CustomType(GraphQLInput):
        __schema__ = gql(
            '''
            input Query {
              hello: String!
              name: String!
            }
            '''
        )

        __out_names__ = {
            "hello": "ok",
            "name": "ok",  # Duplicate out name
        }
except ValueError as e:
    print(e)  # Outputs error regarding duplicate out_names
```

#### 7. Unsupported Default Values

If a default value cannot be represented in the GraphQL schema, a `TypeError` is raised.

```python
class InvalidType:
    pass

try:
    class QueryType(GraphQLInput):
        attr: str = InvalidType()
except TypeError as e:
    print(e)  # Outputs error regarding unsupported default value

try:
    class QueryType(GraphQLInput):
        attr: str = GraphQLInput.field(default_value=InvalidType())
except TypeError as e:
    print(e)  # Outputs error regarding unsupported field default option
```

These validation mechanisms ensure that your `GraphQLInput` types are correctly configured and adhere to GraphQL standards, helping you catch errors early in development.
