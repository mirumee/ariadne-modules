from functools import partial
from typing import Optional, Union

from ariadne import convert_camel_case_to_snake
from graphql import FieldDefinitionNode

from ..types import FieldsDict, InputFieldsDict


def convert_case(
    overrides: Optional[dict] = None,
    *,
    object_fields: Optional[Union[FieldsDict, InputFieldsDict]] = None,
    fields_args: Optional[FieldsDict] = None,
    field_args: Optional[FieldDefinitionNode] = None,
):
    if overrides and not object_fields and not fields_args and not field_args:
        return partial(convert_case, overrides)

    if object_fields:
        return convert_object_fields_case(object_fields, overrides or {})

    if fields_args:
        return convert_fields_args_case(fields_args, overrides or {})

    if field_args:
        return convert_field_args_case(field_args, overrides or {})

    raise ValueError(
        "convert_case was called without any arguments. "
        "If you meant to use it for automatic case conversion, remove call "
        "(convert_case() -> convert_case) or call it with dict of overrides "
        "as only argument."
    )


def convert_object_fields_case(
    fields: Union[FieldsDict, InputFieldsDict], overrides: dict
):
    final_mappings = {}
    for field_name in fields:
        if field_name in overrides:
            field_name_final = overrides[field_name]
        else:
            field_name_final = convert_camel_case_to_snake(field_name)
        if field_name != field_name_final:
            final_mappings[field_name] = field_name_final
    return final_mappings


def convert_fields_args_case(fields: FieldsDict, overrides: dict):
    final_mappings = {}
    for field_name, field_def in fields.items():
        arg_mappings = convert_field_args_case(
            field_def, overrides.get(field_name) or {}
        )
        if arg_mappings:
            final_mappings[field_name] = arg_mappings
    return final_mappings


def convert_field_args_case(field: FieldDefinitionNode, overrides: dict):
    final_mappings = {}
    for arg in field.arguments:
        arg_name = arg.name.value
        if arg_name in overrides:
            arg_name_final = overrides[arg_name]
        else:
            arg_name_final = convert_camel_case_to_snake(arg_name)
        if arg_name != arg_name_final:
            final_mappings[arg_name] = arg_name_final
    return final_mappings
