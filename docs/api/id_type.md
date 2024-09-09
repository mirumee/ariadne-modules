
# `GraphQLID`

The `GraphQLID` class represents a unique identifier in a GraphQL schema. This class is designed to handle ID values in a consistent manner by allowing them to be treated as either strings or integers.

## Class Attributes

- `value`: **str**. This attribute stores the string representation of the ID value.

## Usage

Below is an example of how the `GraphQLID` class can be used to create and compare ID values:

```python
id1 = GraphQLID(123)
id2 = GraphQLID("123")
assert id1 == id2  # True, because both represent the same ID
```

## Methods

### `__init__(self, value: Union[int, str])`
The constructor accepts either an integer or a string and stores it as a string in the `value` attribute.

- **Parameters:**
  - `value` (Union[int, str]): The ID value to be stored.

### `__eq__(self, value: Any) -> bool`
Compares the `GraphQLID` instance with another value. It returns `True` if the other value is either a string, an integer, or another `GraphQLID` instance that represents the same ID.

- **Parameters:**
  - `value` (Any): The value to compare with.
- **Returns:** `bool` - `True` if the values are equal, `False` otherwise.

### `__int__(self) -> int`
Converts the `GraphQLID` value to an integer.

- **Returns:** `int` - The integer representation of the ID.

### `__str__(self) -> str`
Returns the string representation of the `GraphQLID` value.

- **Returns:** `str` - The string representation of the ID.

## Example Use Cases

### 1. Creating IDs
You can create a `GraphQLID` from either an integer or a string, and it will always store the value as a string internally.

```python
id1 = GraphQLID(123)
id2 = GraphQLID("456")
```

### 2. Comparing IDs
The `GraphQLID` class allows for comparison between different types (e.g., integers, strings, or other `GraphQLID` instances) as long as they represent the same ID.

```python
id1 = GraphQLID(123)
id2 = GraphQLID("123")
assert id1 == id2  # True
```

### 3. Converting to Integer or String
You can easily convert a `GraphQLID` to either an integer or a string.

```python
id1 = GraphQLID(789)
print(int(id1))  # Outputs: 789
print(str(id1))  # Outputs: "789"
```

### 4. Using `GraphQLID` in Other Object Types
The `GraphQLID` type can be used as an identifier in other GraphQL object types, allowing you to define unique fields across your schema.

```python
from ariadne_graphql_modules import GraphQLObject, GraphQLID

class Message(GraphQLObject):
    id: GraphQLID
    content: str
    author: str
```

In this example, `Message` is a GraphQL object type where `id` is a `GraphQLID`, ensuring each message has a unique identifier.
