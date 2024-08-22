from ariadne_graphql_modules.v1 import InputType, MutationType, ObjectType, convert_case


def test_cases_are_mapped_for_aliases():
    class ExampleObject(ObjectType):
        __schema__ = """
        type Example {
            field: Int
            otherField: Int
        }
        """
        __aliases__ = convert_case

    assert ExampleObject.__aliases__ == {"otherField": "other_field"}


def test_cases_are_mapped_for_aliases_with_overrides():
    class ExampleObject(ObjectType):
        __schema__ = """
        type Example {
            field: Int
            otherField: Int
        }
        """
        __aliases__ = convert_case({"field": "override"})

    assert ExampleObject.__aliases__ == {
        "field": "override",
        "otherField": "other_field",
    }


def test_cases_are_mapped_for_input_fields():
    class ExampleInput(InputType):
        __schema__ = """
        input Example {
            field: Int
            otherField: Int
        }
        """
        __args__ = convert_case

    assert ExampleInput.__args__ == {"otherField": "other_field"}


def test_cases_are_mapped_for_input_fields_with_overrides():
    class ExampleInput(InputType):
        __schema__ = """
        input Example {
            field: Int
            otherField: Int
        }
        """
        __args__ = convert_case({"field": "override"})

    assert ExampleInput.__args__ == {
        "field": "override",
        "otherField": "other_field",
    }


def test_cases_are_mapped_for_fields_args():
    class ExampleObject(ObjectType):
        __schema__ = """
        type Example {
            field(arg: Int, secondArg: Int): Int
            otherField(arg: Int, thirdArg: Int): Int
        }
        """
        __fields_args__ = convert_case

    assert ExampleObject.__fields_args__ == {
        "field": {
            "secondArg": "second_arg",
        },
        "otherField": {
            "thirdArg": "third_arg",
        },
    }


def test_cases_are_mapped_for_fields_args_with_overrides():
    class ExampleObject(ObjectType):
        __schema__ = """
        type Example {
            field(arg: Int, secondArg: Int): Int
            otherField(arg: Int, thirdArg: Int): Int
        }
        """
        __fields_args__ = convert_case(
            {
                "field": {
                    "arg": "override",
                }
            }
        )

    assert ExampleObject.__fields_args__ == {
        "field": {
            "arg": "override",
            "secondArg": "second_arg",
        },
        "otherField": {
            "thirdArg": "third_arg",
        },
    }


def test_cases_are_mapped_for_mutation_args():
    class ExampleMutation(MutationType):
        __schema__ = """
        type Mutation {
            field(arg: Int, secondArg: Int): Int
        }
        """
        __args__ = convert_case

        @staticmethod
        def resolve_mutation(*_, **__):
            return 42

    assert ExampleMutation.__args__ == {"secondArg": "second_arg"}


def test_cases_are_mapped_for_mutation_args_with_overrides():
    class ExampleMutation(MutationType):
        __schema__ = """
        type Mutation {
            field(arg: Int, secondArg: Int): Int
        }
        """
        __args__ = convert_case(
            {
                "arg": "override",
            }
        )

        @staticmethod
        def resolve_mutation(*_, **__):
            return 42

    assert ExampleMutation.__args__ == {
        "arg": "override",
        "secondArg": "second_arg",
    }
