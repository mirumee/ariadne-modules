[![Ariadne](https://ariadnegraphql.org/img/logo-horizontal-sm.png)](https://ariadnegraphql.org)

[![Build Status](https://github.com/mirumee/ariadne-graphql-modules/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/mirumee/ariadne-graphql-modules/actions)

## ⚠️ Important Migration Warning: Version 1.0.0

With the release of version 1.0.0, there have been significant changes to the `ariadne_graphql_modules` API. If you are upgrading from a previous version, **you will need to update your imports** to ensure your code continues to function correctly.

### What You Need to Do

To maintain compatibility with existing code, you must explicitly import types from the `v1` module of `ariadne_graphql_modules`. This is necessary for any code that relies on the legacy API from versions prior to 1.0.0.

### Example

**Before upgrading:**

```python
from ariadne_graphql_modules import ObjectType, EnumType
```

**After upgrading to 1.0.0:**

```python
from ariadne_graphql_modules.v1 import ObjectType, EnumType
```

### Why This Change?

The introduction of version 1.0.0 brings a more robust and streamlined API, with better support for modular GraphQL schemas. To facilitate this, legacy types and functionality have been moved to the `v1` submodule, allowing new projects to take full advantage of the updated architecture while providing a clear path for migrating existing codebases.

# Ariadne GraphQL Modules

**Ariadne GraphQL Modules** is an extension for the [Ariadne](https://ariadnegraphql.org/) framework, designed to help developers structure and manage GraphQL schemas in a modular way. This library provides an organized approach to building GraphQL APIs by dividing your schema into self-contained, reusable modules, each responsible for its own part of the schema.

## Installation

Ariadne GraphQL Modules can be installed using pip:

```bash
pip install ariadne-graphql-modules
```

Ariadne 0.23 or later is required for the library to work.

## Basic Usage

Here is a basic example of how to use Ariadne GraphQL Modules to create a simple GraphQL API:

```python
from datetime import date

from ariadne.asgi import GraphQL
from ariadne_graphql_modules import ObjectType, gql, make_executable_schema


class Query(ObjectType):
    __schema__ = gql(
        """
        type Query {
            message: String!
            year: Int!
        }
        """
    )

    @staticmethod
    def resolve_message(*_):
        return "Hello world!"

    @staticmethod
    def resolve_year(*_):
        return date.today().year


schema = make_executable_schema(Query)
app = GraphQL(schema=schema, debug=True)
```

In this example, a simple `Query` type is defined within a module. The `make_executable_schema` function is then used to combine the module into a complete schema, which can be used to create a GraphQL server.

