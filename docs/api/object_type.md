
# `GraphQLObject`

The `GraphQLObject` class is a core component of the `ariadne_graphql_modules` library used to define GraphQL object types. This class allows you to create GraphQL objects that represent structured data with fields, interfaces, and custom resolvers. The class also supports schema-based and schema-less definitions.

## Inheritance

- Inherits from `GraphQLBaseObject`.

## Class Attributes

- **`__schema__`**: *(Optional[str])* Holds the GraphQL schema definition string for the object type if provided.
- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL object type.
- **`__description__`**: *(Optional[str])* A description of the object type, included in the GraphQL schema.
- **`__graphql_type__`**: Defines the GraphQL type as `GraphQLClassType.OBJECT`.
- **`__aliases__`**: *(Optional[Dict[str, str]])* Defines field aliases for the object type.
- **`__requires__`**: *(Optional[Iterable[Union[Type[GraphQLType], Type[Enum]]]])* Specifies other types or enums that are required by this object type.

## Core Methods

### `field`

The `field` method is a static method that provides a shortcut for defining fields in a `GraphQLObject`. It allows for custom configuration of fields, including setting a specific name, type, arguments, and a description.

- **Parameters:**
  - `f` (Optional[Resolver]): The resolver function for the field. If not provided, the field will use the default resolver.
  - `name` (Optional[str]): The name of the field in the GraphQL schema. If not provided, the field name defaults to the attribute name in the class.
  - `graphql_type` (Optional[Any]): The GraphQL type of the field. This can be a basic GraphQL type, a custom type, or a list type.
  - `args` (Optional[Dict[str, GraphQLObjectFieldArg]]): A dictionary of arguments that the field can accept.
  - `description` (Optional[str]): A description for the field, which is included in the GraphQL schema.
  - `default_value` (Optional[Any]): A default value for the field.

- **Returns:** A configured field that can be used in a `GraphQLObject`.

**Example Usage:**

```python
class QueryType(GraphQLObject):
    hello: str = GraphQLObject.field(description="Returns a greeting", default_value="Hello World!")
```

### `resolver`

The `resolver` method is a static method used to define a resolver for a specific field in a `GraphQLObject`. The resolver processes the data before returning it to the client.

- **Parameters:**
  - `field` (str): The name of the field for which the resolver is being defined.
  - `graphql_type` (Optional[Any]): The GraphQL type of the field.
  - `args` (Optional[Dict[str, GraphQLObjectFieldArg]]): A dictionary of arguments that the field can accept.
  - `description` (Optional[str]): A description for the resolver, which is included in the GraphQL schema.

- **Returns:** A decorator that can be used to wrap a function, making it a resolver for the specified field.

**Example Usage:**

```python
class QueryType(GraphQLObject):
    hello: str

    @GraphQLObject.resolver("hello")
    def resolve_hello(*_):
        return "Hello World!"
```

### `argument`

The `argument` method is a static method used to define an argument for a field in a `GraphQLObject`. This method is particularly useful for adding descriptions and default values to arguments.

- **Parameters:**
  - `name` (Optional[str]): The name of the argument.
  - `description` (Optional[str]): A description for the argument.
  - `graphql_type` (Optional[Any]): The GraphQL type of the argument.
  - `default_value` (Optional[Any]): A default value for the argument.

- **Returns:** A `GraphQLObjectFieldArg` instance that represents the argument.

**Example Usage:**

```python
class QueryType(GraphQLObject):
    @GraphQLObject.field(
        args={"message": GraphQLObject.argument(description="Message to echo", graphql_type=str)}
    )
    def echo_message(obj, info, message: str) -> str:
        return message
```

## Inheritance Feature and Interface Implementation

The `GraphQLObject` class supports inheritance, allowing you to extend existing object types or interfaces. This feature enables you to reuse and extend functionality across multiple object types, enhancing modularity and code reuse.

### Inheriting from `GraphQLInterface`

When you inherit from a `GraphQLInterface`, the resulting object type will automatically include an `implements` clause in the GraphQL schema. This means the object type will implement all the fields defined by the interface.

```python
from ariadne_graphql_modules import GraphQLObject, GraphQLInterface

class NodeInterface(GraphQLInterface):
    id: str

class UserType(GraphQLObject, NodeInterface):
    name: str
```

In this example, `UserType` will implement the `Node` interface, and the GraphQL schema will include `type User implements Node`.

### Inheriting from Another Object Type

When you inherit from another `GraphQLObject`, the derived class will inherit all attributes, resolvers, and custom fields from the base object type. However, the derived object type will not include an `implements` clause in the schema.

```python
class BaseCategoryType(GraphQLObject):
    name: str
    description: str

class CategoryType(BaseCategoryType):
    posts: int
```

In this example, `CategoryType` inherits the `name` and `description` fields from `BaseCategoryType`, along with any custom resolvers or field configurations.

## Example Usage

### Defining an Object Type

To define an object type, subclass `GraphQLObject` and specify fields using class attributes.

```python
from ariadne_graphql_modules import GraphQLObject, GraphQLID

class CategoryType(GraphQLObject):
    name: str
    posts: int
```

### Using a Schema to Define an Object Type

You can define an object type using a GraphQL schema by setting the `__schema__` attribute.

```python
from ariadne import gql
from ariadne_graphql_modules import GraphQLObject

class CategoryType(GraphQLObject):
    __schema__ = gql(
        """
        type Category {
            name: String
            posts: Int
        }
        """
    )

    name: str
    posts: int
```

### Adding Resolvers to an Object Type

You can add custom resolvers to fields in an object type by using the `@GraphQLObject.resolver` decorator.

```python
class QueryType(GraphQLObject):
    hello: str

    @GraphQLObject.resolver("hello")
    def resolve_hello(*_):
        return "Hello World!"
```

### Handling Aliases in Object Types

You can define aliases for fields in an object type using the `__aliases__` attribute.

```python
class CategoryType(GraphQLObject):
    __aliases__ = {"name": "title"}

    title: str
    posts: int
```

## Validation

The `GraphQLObject` class includes validation mechanisms to ensure that object types are correctly defined. Validation is performed both for schema-based and schema-less object types.

### Validation Process

1. **Type Checking**: Ensures that the class is of the correct GraphQL type (`OBJECT`).
2. **Schema Parsing and Validation**: If a schema is provided, it is parsed and validated against the class definition.
3. **Field and Alias Validation**: Ensures that all fields and aliases are correctly defined and do not conflict.

### Validation Example

Here is an example where validation checks that the provided schema matches the class definition:

```python
from graphql import gql
from ariadne_graphql_modules import GraphQLObject

class CategoryType(GraphQLObject):
    __schema__ = gql(
        """
        type Category {
            name: String
            posts: Int
        }
        """
    )

    name: str
    posts: int
```

If the class definition and the schema do not match, a `ValueError` will be raised.

## Example: Using a Field with a Custom Resolver

```python
from ariadne_graphql_modules import GraphQLObject

class QueryType(GraphQLObject):
    @GraphQLObject.field()
    def hello(obj, info) -> str:
        return "Hello World!"
```

This method will resolve the `hello` field to return `"Hello World!"`.