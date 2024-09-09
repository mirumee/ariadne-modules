
# `GraphQLSubscription`

The `GraphQLSubscription` class is designed to facilitate the creation and management of GraphQL subscriptions within a schema. Subscriptions in GraphQL allow clients to receive real-time updates when specific events occur.

## Inheritance

- Inherits from `GraphQLBaseObject`.

## Class Attributes

- **`__schema__`**: *(Optional[str])* - The GraphQL schema definition string for the union, if provided.
- **`__graphql_name__`**: *(Optional[str])* The custom name for the GraphQL type. If not provided, it will be generated based on the class name.
- **`__description__`**: *(Optional[str])* A description of the GraphQL type, included in the schema documentation.
- **`__graphql_type__`**: Defines the GraphQL class type, set to `GraphQLClassType.BASE`.
- **`__aliases__`**: *(Optional[Dict[str, str]])* Defines field aliases for the object type.
- **`__requires__`**: *(Optional[Iterable[Union[Type[GraphQLType], Type[Enum]]]])* Specifies other types or enums that are required by this object type.

## Class Methods and Decorators

### `source`

Defines a source for a subscription. The source is an async generator that yields the data to be sent to clients.
- **Parameters:**
  - `field: str`: The name of the subscription field.
  - `graphql_type: Optional[Any]`: The GraphQL type of the field.
  - `args: Optional[Dict[str, GraphQLObjectFieldArg]]`: Optional arguments that the subscription can accept.
  - `description: Optional[str]`: An optional description for the subscription field.

### `resolver`

Defines a resolver for a subscription. The resolver processes the data provided by the source before sending it to the client.

- **Parameters:**
  - `field: str`: The name of the resolver field.

### `field`

Defines a field in the subscription type. This is a shortcut for defining subscription fields without a full schema.

- **Parameters:**
  - `name: Optional[str]`: The name of the field that will be created.

## Field Definition Limitations

In `GraphQLSubscription`, detailed field definitions, such as specifying arguments or custom types, must be done using the `source` method. This ensures that the source and resolver methods are properly aligned and that the subscription functions as expected.

## Inheritance feature

`GraphQLSubscription` does not support inheritance from other subscription classes. Each subscription class must define its fields and logic independently. This limitation is intentional to prevent issues with overlapping field definitions and resolver conflicts.

## Example

### Basic Subscription

Define a simple subscription that notifies clients whenever a new message is added:

```python
from ariadne_graphql_modules import GraphQLSubscription, GraphQLObject, make_executable_schema

class Message(GraphQLObject):
    id: GraphQLID
    content: str
    author: str

class SubscriptionType(GraphQLSubscription):
    message_added: Message

    @GraphQLSubscription.source("message_added", graphql_type=Message)
    async def message_added_generator(obj, info):
        while True:
            yield {"id": "some_id", "content": "message", "author": "Anon"}

    @GraphQLSubscription.resolver("message_added")
    async def resolve_message_added(message, info):
        return message

schema = make_executable_schema(SubscriptionType)
```

### Subscriptions with Arguments

Handle subscriptions that accept arguments:

```python
class SubscriptionType(GraphQLSubscription):

    @GraphQLSubscription.source(
        "message_added",
        args={"channel": GraphQLObject.argument(description="Lorem ipsum.")},
        graphql_type=Message,
    )
    async def message_added_generator(obj, info, channel: GraphQLID):
        while True:
            yield {"id": "some_id", "content": f"message_{channel}", "author": "Anon"}

    @GraphQLSubscription.field()
    def message_added(message, info, channel: GraphQLID):
        return message
```

### Schema-based Subscription

Define a subscription using a GraphQL schema:

```python
from ariadne import gql

class SubscriptionType(GraphQLSubscription):
    __schema__ = gql(
        '''
        type Subscription {
            messageAdded: Message!
        }
        '''
    )

    @GraphQLSubscription.source("messageAdded", graphql_type=Message)
    async def message_added_generator(obj, info):
        while True:
            yield {"id": "some_id", "content": "message", "author": "Anon"}

    @GraphQLSubscription.resolver("messageAdded")
    async def resolve_message_added(message, info):
        return message
```

## Validation

Validation in `GraphQLSubscription` works similarly to that in `GraphQLObject`. The following validation checks are performed:

- **Field Definitions**: Fields must be properly defined, either through SDL in the `__schema__` attribute or directly within the class using the `source` and `resolver` decorators.
- **Schema Consistency**: The schema is checked for consistency, ensuring that all fields and their types are correctly defined.
- **Field Names**: The field names defined in the subscription must match those in the schema.

If any of these checks fail, a `ValueError` will be raised during schema construction.
