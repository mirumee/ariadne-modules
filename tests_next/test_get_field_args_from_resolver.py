from ariadne_graphql_modules.next.graphql_object import get_field_args_from_resolver


def test_field_has_no_args_after_obj_and_info_args():
    def field_resolver(obj, info):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert not field_args


def test_field_has_no_args_in_resolver_with_catch_all_args_list():
    def field_resolver(*_):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert not field_args


def test_field_has_arg_after_excess_positional_args():
    def field_resolver(*_, name):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert len(field_args) == 1

    field_arg = field_args["name"]
    assert field_arg.name == "name"
    assert field_arg.out_name == "name"
    assert field_arg.field_type is None


def test_field_has_arg_after_positional_args_separator():
    def field_resolver(obj, info, *, name):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert len(field_args) == 1

    field_arg = field_args["name"]
    assert field_arg.name == "name"
    assert field_arg.out_name == "name"
    assert field_arg.field_type is None


def test_field_has_arg_after_obj_and_info_args():
    def field_resolver(obj, info, name):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert len(field_args) == 1

    field_arg = field_args["name"]
    assert field_arg.name == "name"
    assert field_arg.out_name == "name"
    assert field_arg.field_type is None


def test_field_has_multiple_args_after_excess_positional_args():
    def field_resolver(*_, name, age_cutoff: int):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert len(field_args) == 2

    name_arg = field_args["name"]
    assert name_arg.name == "name"
    assert name_arg.out_name == "name"
    assert name_arg.field_type is None

    age_arg = field_args["age_cutoff"]
    assert age_arg.name == "ageCutoff"
    assert age_arg.out_name == "age_cutoff"
    assert age_arg.field_type is int


def test_field_has_multiple_args_after_positional_args_separator():
    def field_resolver(obj, info, *, name, age_cutoff: int):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert len(field_args) == 2

    name_arg = field_args["name"]
    assert name_arg.name == "name"
    assert name_arg.out_name == "name"
    assert name_arg.field_type is None

    age_arg = field_args["age_cutoff"]
    assert age_arg.name == "ageCutoff"
    assert age_arg.out_name == "age_cutoff"
    assert age_arg.field_type is int


def test_field_has_multiple_args_after_obj_and_info_args():
    def field_resolver(obj, info, name, age_cutoff: int):
        pass

    field_args = get_field_args_from_resolver(field_resolver)
    assert len(field_args) == 2

    name_arg = field_args["name"]
    assert name_arg.name == "name"
    assert name_arg.out_name == "name"
    assert name_arg.field_type is None

    age_arg = field_args["age_cutoff"]
    assert age_arg.name == "ageCutoff"
    assert age_arg.out_name == "age_cutoff"
    assert age_arg.field_type is int


def test_field_has_arg_after_obj_and_info_args_on_class_function():
    class CustomObject:
        def field_resolver(obj, info, name):
            pass

    field_args = get_field_args_from_resolver(CustomObject.field_resolver)
    assert len(field_args) == 1

    field_arg = field_args["name"]
    assert field_arg.name == "name"
    assert field_arg.out_name == "name"
    assert field_arg.field_type is None


def test_field_has_arg_after_obj_and_info_args_on_class_method():
    class CustomObject:
        @classmethod
        def field_resolver(cls, obj, info, name):
            pass

    field_args = get_field_args_from_resolver(CustomObject.field_resolver)
    assert len(field_args) == 1

    field_arg = field_args["name"]
    assert field_arg.name == "name"
    assert field_arg.out_name == "name"
    assert field_arg.field_type is None


def test_field_has_arg_after_obj_and_info_args_on_static_method():
    class CustomObject:
        @staticmethod
        def field_resolver(obj, info, name):
            pass

    field_args = get_field_args_from_resolver(CustomObject.field_resolver)
    assert len(field_args) == 1

    field_arg = field_args["name"]
    assert field_arg.name == "name"
    assert field_arg.out_name == "name"
    assert field_arg.field_type is None
