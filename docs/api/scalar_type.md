# `GraphQLScalar`

The `GraphQLScalar` class is a generic base class in the `ariadne_graphql_modules` library used to define custom scalar types in GraphQL. Scalars in GraphQL represent primitive data types like `Int`, `Float`, `String`, `Boolean`, etc. This class provides the framework for creating custom scalars with serialization and parsing logic.

## Inheritance

- Inherits from `GraphQLType` and `Generic[T]`.

## Class Attributes

- **`__schema__`**: *(Optional[str])* - The GraphQL schema definition string for the union, if provided.
- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL type. If not provided, it will be generated based on the class name.
- **`__description__`**: *(Optional[str])* A description of the GraphQL type, included in the schema documentation.
- **`wrapped_value`** (T): Stores the value wrapped by the scalar.

## Initialization

### `__init__(self, value: T)`

- **Parameters:**
  - `value` (T): The value to be wrapped by the scalar instance. Saved on `wrapped_value` class attribute

## Class Methods

### `serialize`

Serializes the scalar's value. If the value is an instance of the scalar, it unwraps the value before serialization.

- **Parameters:**
  - `value: Any`: The value to serialize.

### `parse_value`

Parses the given value, typically used when receiving input from a GraphQL query.

- **Parameters:**
  - `value: Any`: The value to parse.

### `parse_literal`

Parses a literal GraphQL value. This method is used to handle literals in GraphQL queries.

- **Parameters:**
  - `node: ValueNode`: The AST node representing the value.
  - `variables: (Optional[Dict[str, Any]])`: A dictionary of variables in the GraphQL query.

## Example

### Defining a Custom Scalar

To define a custom scalar, subclass `GraphQLScalar` and implement the required serialization and parsing methods.

```python
from datetime import date
from ariadne_graphql_modules import GraphQLScalar

class DateScalar(GraphQLScalar[date]):
    @classmethod
    def serialize(cls, value):
        if isinstance(value, cls):
            return str(value.unwrap())
        return str(value)
```

### Using a Custom Scalar in a Schema

```python
from ariadne_graphql_modules import GraphQLObject, make_executable_schema

class QueryType(GraphQLObject):
    date: DateScalar

    @GraphQLObject.resolver("date")
    def resolve_date(*_) -> DateScalar:
        return DateScalar(date(1989, 10, 30))

schema = make_executable_schema(QueryType)
```

### Handling Scalars with and without Schema

You can define a scalar with or without an explicit schema definition:

```python
class SchemaDateScalar(GraphQLScalar[date]):
    __schema__ = "scalar Date"
    
    @classmethod
    def serialize(cls, value):
        if isinstance(value, cls):
            return str(value.unwrap())
        return str(value)
```

### Using `parse_value` and `parse_literal`

The `parse_value` and `parse_literal` methods are crucial for processing input values in GraphQL queries. They ensure that the values provided by the client are correctly interpreted according to the scalar's logic.

#### Example: `parse_value`

The `parse_value` method is typically used to convert input values from GraphQL queries into the appropriate type for use in the application.

```python
class DateScalar(GraphQLScalar[str]):
    @classmethod
    def parse_value(cls, value):
        # Assume value is a string representing a date, e.g., "2023-01-01"
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {value}")

# Example usage in a query
parsed_date = DateScalar.parse_value("2023-01-01")
print(parsed_date)  # Outputs: 2023-01-01 as a `date` object
```

In this example, `parse_value` converts a string into a `date` object. If the string does not match the expected format, an error is raised.

#### Example: `parse_literal`

The `parse_literal` method is used to handle literal values directly from the GraphQL query's Abstract Syntax Tree (AST). This is useful when dealing with inline values in queries.

```python
from graphql import StringValueNode

class DateScalar(GraphQLScalar[str]):
    @classmethod
    def parse_literal(cls, node, variables=None):
        if isinstance(node, StringValueNode):
            return cls.parse_value(node.value)
        raise ValueError("Invalid AST node type")

# Example usage in a query
parsed_date = DateScalar.parse_literal(StringValueNode(value="2023-01-01"))
print(parsed_date)  # Outputs: 2023-01-01 as a `date` object
```

In this example, `parse_literal` checks if the AST node is of the correct type (`StringValueNode`) and then applies the `parse_value` logic to convert it.

### Validation

The `GraphQLScalar` class includes a validation mechanism to ensure that custom scalar types are correctly defined and conform to GraphQL standards. This validation is especially important when defining a scalar with an explicit schema using the `__schema__` attribute.

#### Validation Process

When a custom scalar class defines a schema using the `__schema__` attribute, the following validation steps occur:

1. **Schema Parsing**: The schema string is parsed to ensure it corresponds to a valid GraphQL scalar type.
2. **Type Checking**: The parsed schema is checked to confirm it is of the correct type (`ScalarTypeDefinitionNode`).
3. **Name Validation**: The scalar's name is validated to ensure it adheres to GraphQL naming conventions.
4. **Description Validation**: The scalar's description is validated to ensure it is consistent and correctly formatted.
