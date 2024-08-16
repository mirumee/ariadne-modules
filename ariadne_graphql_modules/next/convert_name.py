def convert_python_name_to_graphql(python_name: str) -> str:
    components = python_name.split("_")
    return components[0].lower() + "".join(x.capitalize() for x in components[1:])


def convert_graphql_name_to_python(graphql_name: str) -> str:
    python_name = ""
    for c in graphql_name:
        if c.isupper() or c.isdigit():
            python_name += "_" + c.lower()
        else:
            python_name += c
    return python_name.lstrip("_")
