
## `make_executable_schema`

The `make_executable_schema` function constructs an executable GraphQL schema from a list of types, including custom types, SDL strings, and various other GraphQL elements. This function also validates the types for consistency and allows for customization through options like `convert_names_case` and `merge_roots`.

### Basic Usage

```python
class UserType(GraphQLObject):
    __schema__ = """
    type User {
        id: ID!
        username: String!
    }
    """


class QueryType(GraphQLObject):
    __schema__ = """
    type Query {
        user: User
    }
    """
    __requires__ = [UserType]

    @staticmethod
    def user(*_):
        return {
            "id": 1,
            "username": "Alice",
        }


schema = make_executable_schema(QueryType)
```

### Automatic Merging of Roots

By default, when multiple `Query`, `Mutation`, or `Subscription` types are passed to `make_executable_schema`, they are merged into a single type containing all the fields from the provided definitions, ordered alphabetically by field name.

```python
class UserQueriesType(GraphQLObject):
    __schema__ = """
    type Query {
        user(id: ID!): User
    }
    """


class ProductsQueriesType(GraphQLObject):
    __schema__ = """
    type Query {
        product(id: ID!): Product
    }
    """

schema = make_executable_schema(UserQueriesType, ProductsQueriesType)
```

This will result in a single `Query` type in the schema:

```graphql
type Query {
    product(id: ID!): Product
    user(id: ID!): User
}
```

To disable this behavior, you can use the `merge_roots=False` option:

```python
schema = make_executable_schema(
    UserQueriesType,
    ProductsQueriesType,
    merge_roots=False,
)
```

### Name Conversion with `convert_names_case`

The `convert_names_case` option allows you to apply custom naming conventions to the types, fields, and other elements within the schema. When this option is enabled, it triggers the `convert_schema_names` function.

```python
def uppercase_name_converter(name: str, schema: GraphQLSchema, path: Tuple[str, ...]) -> str:
    return name.upper()

schema = make_executable_schema(QueryType, convert_names_case=uppercase_name_converter)
```

#### How `convert_schema_names` Works

The `convert_schema_names` function traverses the schema and applies a given `SchemaNameConverter` to rename elements according to custom logic. The converter is a callable that receives the original name, the schema, and the path to the element, and it returns the new name.

- **`schema`**: The GraphQL schema being modified.
- **`converter`**: A callable that transforms the names based on your custom logic.

The function ensures that all types, fields, and other schema elements adhere to the naming conventions specified by your converter function.

#### Example

If `convert_names_case` is set to `True`, the function will automatically convert names to the convention defined by the `SchemaNameConverter`. For instance, you might convert all names to uppercase:

```python
def uppercase_converter(name: str, schema: GraphQLSchema, path: Tuple[str, ...]) -> str:
    return name.upper()

schema = make_executable_schema(QueryType, convert_names_case=uppercase_converter)
```

This would convert all type and field names in the schema to uppercase.
