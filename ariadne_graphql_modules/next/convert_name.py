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