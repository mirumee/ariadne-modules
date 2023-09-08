import pytest
from graphql import parse

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next.validators import validate_description


def test_description_validator_passes_type_without_description():
    class CustomType:
        pass

    validate_description(CustomType, parse("scalar Custom").definitions[0])


def test_description_validator_passes_type_with_description_attr():
    class CustomType:
        __description__ = "Example scalar"

    validate_description(CustomType, parse("scalar Custom").definitions[0])


def test_description_validator_raises_error_for_type_with_two_descriptions(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType:
            __description__ = "Example scalar"

        validate_description(
            CustomType,
            parse(
                """
                \"\"\"Lorem ipsum\"\"\"
                scalar Custom
                """
            ).definitions[0],
        )

    snapshot.assert_match(str(exc_info.value))
