def convert_python_name_to_graphql(python_name: str) -> str:
    final_name = ""
    for i, c in enumerate(python_name):
        if not i:
            final_name += c.lower()
        else:
            if c == "_":
                continue
            if python_name[i - 1] == "_":
                final_name += c.upper()
            else:
                final_name += c.lower()

    return final_name


def convert_graphql_name_to_python(graphql_name: str) -> str:
    final_name = ""
    for i, c in enumerate(graphql_name.lower()):
        if not i:
            final_name += c
        else:
            if final_name[-1] != "_" and (c != graphql_name[i] or c.isdigit()):
                final_name += "_"
            final_name += c

    return final_name
