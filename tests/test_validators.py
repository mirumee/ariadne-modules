import pytest
from graphql import parse

from ariadne_graphql_modules.validators import validate_description, validate_name


def test_description_validator_passes_type_without_description():
    class CustomType:
        pass

    validate_description(CustomType, parse("scalar Custom").definitions[0])  # type: ignore


def test_description_validator_passes_type_with_description_attr():
    class CustomType:
        __description__ = "Example scalar"

    validate_description(CustomType, parse("scalar Custom").definitions[0])  # type: ignore


def test_description_validator_raises_error_for_type_with_two_descriptions(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType:
            __description__ = "Example scalar"

        validate_description(
            CustomType,  # type: ignore
            parse(
                """
                \"\"\"Lorem ipsum\"\"\"
                scalar Custom
                """
            ).definitions[0],
        )

    data_regression.check(str(exc_info.value))


def test_name_validator_passes_type_without_explicit_name():
    class CustomType:
        pass

    validate_name(CustomType, parse("type Custom").definitions[0])  # type: ignore


def test_name_validator_passes_type_with_graphql_name_attr_matching_definition():
    class CustomType:
        __graphql_name__ = "Custom"

    validate_name(CustomType, parse("type Custom").definitions[0])  # type: ignore


def test_name_validator_raises_error_for_name_and_definition_mismatch(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType:
            __graphql_name__ = "Example"

        validate_name(
            CustomType,  # type: ignore
            parse("type Custom").definitions[0],
        )

    data_regression.check(str(exc_info.value))
