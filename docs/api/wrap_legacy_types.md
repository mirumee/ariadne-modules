
# `wrap_legacy_types`

The `wrap_legacy_types` function is part of the `ariadne_graphql_modules` library and provides a way to migrate legacy GraphQL types from version 1 of the library to be compatible with the newer version. This function wraps the legacy types in a way that they can be used seamlessly in the new system without rewriting their definitions.

## Function Signature

```python
def wrap_legacy_types(
    *bindable_types: Type[BaseType],
) -> List[Type["LegacyGraphQLType"]]:
```

## Parameters

- `*bindable_types`: A variable number of legacy GraphQL type classes (from v1 of the library) that should be wrapped to work with the newer version of the library.

  - **Type:** `Type[BaseType]`
  - **Description:** Each of these types could be one of the legacy types such as `ObjectType`, `InterfaceType`, `UnionType`, etc.

## Returns

- **List[Type["LegacyGraphQLType"]]:** A list of new classes that inherit from `LegacyGraphQLType`, each corresponding to one of the legacy types passed in as arguments.

## Usage Example

Here’s an example of how to use the `wrap_legacy_types` function:

```python
from ariadne_graphql_modules.compatibility_layer import wrap_legacy_types
from ariadne_graphql_modules.v1.object_type import ObjectType
from ariadne_graphql_modules.v1.enum_type import EnumType

class FancyObjectType(ObjectType):
    __schema__ = '''
    type FancyObject {
        id: ID!
        someInt: Int!
        someFloat: Float!
        someBoolean: Boolean!
        someString: String!
    }
    '''

class UserRoleEnum(EnumType):
    __schema__ = '''
    enum UserRole {
        USER
        MOD
        ADMIN
    }
    '''

wrapped_types = wrap_legacy_types(FancyObjectType, UserRoleEnum)
```

## Detailed Example

### Wrapping and Using Legacy Types in Schema

```python
from ariadne_graphql_modules.compatibility_layer import wrap_legacy_types
from ariadne_graphql_modules.v1.object_type import ObjectType
from ariadne_graphql_modules.v1.scalar_type import ScalarType
from ariadne_graphql_modules.executable_schema import make_executable_schema

class DateScalar(ScalarType):
    __schema__ = "scalar Date"

    @staticmethod
    def serialize(value):
        return value.isoformat()

    @staticmethod
    def parse_value(value):
        return datetime.strptime(value, "%Y-%m-%d").date()

class QueryType(ObjectType):
    __schema__ = '''
    type Query {
        today: Date!
    }
    '''
    
    @staticmethod
    def resolve_today(*_):
        return date.today()

wrapped_types = wrap_legacy_types(QueryType, DateScalar)
schema = make_executable_schema(*wrapped_types)
```

In this example, `QueryType` and `DateScalar` are legacy types that have been wrapped and used to create an executable schema compatible with the new version of the library.
