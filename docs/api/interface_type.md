
# `GraphQLInterface`

`GraphQLInterface` is a base class used to define GraphQL interfaces in a modular and reusable manner. It provides a structured way to create interfaces with fields, resolvers, and descriptions, making it easier to manage complex GraphQL schemas.

## Inheritance

- Inherits from `GraphQLBaseObject`.

## Class Attributes

- **`__schema__`**: *(Optional[str])* - The GraphQL schema definition string for the union, if provided.
- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL type. If not provided, it will be generated based on the class name.
- **`__description__`**: *(Optional[str])* A description of the GraphQL type, included in the schema documentation.
- **`__graphql_type__`**: Defines the GraphQL class type, set to `GraphQLClassType.BASE`.
- **`__aliases__`**: *(Optional[Dict[str, str]])* Defines field aliases for the object type.
- **`__requires__`**: *(Optional[Iterable[Union[Type[GraphQLType], Type[Enum]]]])* Specifies other types or enums that are required by this object type.

## Core Methods

### `resolve_type`

A static method that resolves the type of an object when using interfaces or unions. This method can be overridden to provide custom type resolution logic.

### `resolver`

Defines a resolver for a subscription. The resolver processes the data provided by the source before sending it to the client.

- **Parameters:**
  - `field: str`: The name of the resolver field.

### `field`

Defines a field in the subscription type. This is a shortcut for defining subscription fields without a full schema.

- **Parameters:**
  - `name: Optional[str]`: The name of the field that will be created.

## Inheritance feature

The `GraphQLInterface` class supports inheritance, allowing interfaces to extend other interfaces. This enables the creation of complex and reusable schemas by composing interfaces from other interfaces.

- **Interface Inheritance**: When an interface inherits from another interface, it automatically implements the inherited interface, and the `implements` clause will be included in the GraphQL schema.
- **Inheritance Example**:

```python
class BaseInterface(GraphQLInterface):
    summary: str

class AdvancedInterface(BaseInterface):
    details: str
```

In this example, `AdvancedInterface` inherits from `BaseInterface`, meaning it will include all fields and logic from `BaseInterface`, and the resulting schema will reflect that `AdvancedInterface` implements `BaseInterface`.

## Example

### Basic Interface Definition

Here’s how to define a basic interface using `GraphQLInterface`:

```python
from ariadne_graphql_modules import GraphQLInterface

class UserInterface(GraphQLInterface):
    summary: str
    score: int
```

### Interface with Schema Definition

You can define the interface schema directly using SDL:

```python
class UserInterface(GraphQLInterface):
    __schema__ = '''
    interface UserInterface {
        summary: String!
        score: Int!
    }
    '''
```

### Custom Type Resolution

You can implement custom logic for resolving types when using the interface:

```python
class UserInterface(GraphQLInterface):
    @staticmethod
    def resolve_type(obj, *_):
        if isinstance(obj, UserType):
            return "UserType"
        raise ValueError(f"Cannot resolve type for object {obj}.")
```

## Validation

The `GraphQLInterface` class includes validation logic to ensure that the defined interface schema is correct and consistent with the class attributes. This validation process includes:

- **Schema Validation**: If the `__schema__` attribute is defined, it is parsed and validated to ensure that it corresponds to a valid GraphQL interface.
- **Name and Description Validation**: Validates that the names and descriptions of the interface and its fields are consistent with GraphQL conventions.
- **Field Validation**: Ensures that all fields defined in the schema have corresponding attributes in the class, and that their types and default values are valid.

### Validation Example

If the schema definition or fields are not correctly defined, a `ValueError` will be raised during the validation process:

```python
from ariadne_graphql_modules import GraphQLInterface

class InvalidInterface(GraphQLInterface):
    __schema__ = '''
    interface InvalidInterface {
        summary: String!
        invalidField: NonExistentType!
    }
    '''
```
