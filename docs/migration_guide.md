# Migration Guide

## `ariadne_graphql_modules.v1` to Current Version

This guide provides a streamlined process for migrating your code from `ariadne_graphql_modules.v1` to the current version. The focus is on maintaining compatibility using the `wrap_legacy_types` function, which allows you to transition smoothly without needing to rewrite your entire codebase.

## Migration Overview

### Wrapping Legacy Types

To maintain compatibility with the current version, all legacy types from `ariadne_graphql_modules.v1` can be wrapped using the `wrap_legacy_types` function. This approach allows you to continue using your existing types with minimal changes.

### Example:

```python
from ariadne_graphql_modules.v1 import ObjectType, EnumType
from ariadne_graphql_modules import make_executable_schema, wrap_legacy_types, GraphQLObject

# Your existing types can remain as is
class QueryType(ObjectType):
    ...
    
class UserRoleEnum(EnumType):
    ...

# You can mix new types with old types
class NewType(GraphQLObject):
    ...

# Wrap them for the new system
my_legacy_types = wrap_legacy_types(QueryType, UserRoleEnum)
schema = make_executable_schema(*my_legacy_types, NewType)
```


### Encouragement to Migrate

While `wrap_legacy_types` provides a quick solution, it is recommended to gradually transition to the current version’s types for better support and new features.
