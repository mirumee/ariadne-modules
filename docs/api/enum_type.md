# `GraphQLEnum`

`GraphQLEnum` is a base class for defining GraphQL enum types in a modular and reusable manner. It allows for the creation of enums using Python's `Enum` class or custom mappings, providing flexibility and ease of integration into your GraphQL schema.

## Inheritance

- Inherits from `GraphQLType`.

## Attributes

- **`__schema__`**: *(Optional[str])* Holds the GraphQL schema definition string for the object type if provided.
- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL object type.
- **`__description__`**: *(Optional)* A description for the enum, which is included in the schema.
- **`__members__`**: Specifies the members of the enum. This can be a Python `Enum`, a dictionary, or a list of strings.
- **`__members_descriptions__`**: *(Optional)* A dictionary mapping enum members to their descriptions.


### `graphql_enum` Function

The `graphql_enum` function is a decorator that simplifies the process of converting a Python `Enum` class into a GraphQL enum type. This function allows you to specify additional properties such as the GraphQL enum's name, description, and member descriptions, as well as control which members are included or excluded in the GraphQL schema.

#### Parameters

- **`cls`**: *(Optional[Type[Enum]])*  
  The Python `Enum` class that you want to convert to a GraphQL enum. This parameter is optional because the function can be used as a decorator.

- **`name`**: *(Optional[str])*  
  The name of the GraphQL enum. If not provided, the name of the `Enum` class will be used.

- **`description`**: *(Optional[str])*  
  A description for the GraphQL enum, which will be included in the schema.

- **`members_descriptions`**: *(Optional[Dict[str, str]])*  
  A dictionary mapping enum members to their descriptions. This allows for detailed documentation of each enum member in the GraphQL schema.

- **`members_include`**: *(Optional[Iterable[str]])*  
  A list of member names to include in the GraphQL enum. If not provided, all members of the `Enum` will be included.

- **`members_exclude`**: *(Optional[Iterable[str]])*  
  A list of member names to exclude from the GraphQL enum. This allows you to omit specific members from the GraphQL schema.

#### Returns

- **`graphql_enum_decorator`**: *(Callable)*  
  A decorator function that attaches a `__get_graphql_model__` method to the `Enum` class. This method returns the GraphQL model for the enum, making it ready to be integrated into your GraphQL schema.

## Usage Examples

### Basic Enum Definition

Here’s how to define a basic enum type using `GraphQLEnum` with a Python `Enum`:

```python
from enum import Enum
from ariadne_graphql_modules import GraphQLEnum

class UserLevelEnum(Enum):
    GUEST = 0
    MEMBER = 1
    ADMIN = 2

class UserLevel(GraphQLEnum):
    __members__ = UserLevelEnum
```

### Enum with Custom Schema

You can define the enum schema directly using SDL:

```python
class UserLevel(GraphQLEnum):
    __schema__ = """
    enum UserLevel {
        GUEST
        MEMBER
        ADMIN
    }
    """
    __members__ = UserLevelEnum
```

### Enum with Descriptions

You can add descriptions to both the enum and its members:

```python
class UserLevel(GraphQLEnum):
    __description__ = "User access levels."
    __members__ = UserLevelEnum
    __members_descriptions__ = {
        "MEMBER": "A registered user.",
        "ADMIN": "An administrator with full access."
    }
```

### Example Usage of *graphql_enum* function

Here’s an example of how to use the `graphql_enum` decorator:

```python
from enum import Enum
from ariadne_graphql_modules import graphql_enum

@graphql_enum
class SeverityLevel(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

# Access the GraphQL model
graphql_model = SeverityLevel.__get_graphql_model__()

# The GraphQL model can now be used in your schema
```

In this example:

- The `SeverityLevel` enum is decorated with `graphql_enum`, automatically converting it into a GraphQL enum.
- The `__get_graphql_model__` method is added to `SeverityLevel`, which returns the GraphQL model, including the enum name, members, and corresponding AST.

This function allows for an easy transition from Python enums to GraphQL enums, providing flexibility in customizing the GraphQL schema with descriptions and member selections.
