# deferred

This module provides a mechanism to defer type information, particularly useful for handling forward references and circular dependencies in Python modules. The key components include the `DeferredTypeData` data class and the `deferred` function.

## deferred Function

The `deferred` function creates a `DeferredTypeData` object from a given module path. If the module path is relative (i.e., starts with a '.'), the function resolves it based on the caller's package context.

### Parameters

- `module_path` (str): The module path where the deferred type resides. This can be an absolute or a relative path.

### Example Usage

```python
from ariadne_graphql_modules import deferred

# Deferring a type with an absolute module path
deferred_type = deferred('some_module.TypeName')

# Deferring a type with a relative module path
deferred_type_relative = deferred('.TypeName')
```

### Error Handling

- Raises `RuntimeError` if the `deferred` function is not called within a class attribute definition context.
- Raises `ValueError` if the relative module path points outside of the current package.

### Advanced Usage Example

This example demonstrates how to use the `deferred` function with `Annotated` for forward type references within a `GraphQLObject`.

```python
from typing import TYPE_CHECKING, Annotated
from ariadne_graphql_modules import GraphQLObject, deferred

if TYPE_CHECKING:
    from .types import ForwardScalar

class MockType(GraphQLObject):
    field: Annotated["ForwardScalar", deferred("tests.types")]
```

In this example, the `deferred` function is used in conjunction with `Annotated` to specify that the `field` in `MockType` references a type (`ForwardScalar`) that is defined in the `tests.types` module. This approach is particularly useful when dealing with forward references or circular dependencies in type annotations.
