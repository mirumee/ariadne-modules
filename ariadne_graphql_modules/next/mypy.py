from mypy.plugin import Plugin, MethodContext  # pylint: disable=E0611
from mypy.types import Instance  # pylint: disable=E0611
from mypy.nodes import EllipsisExpr  # pylint: disable=E0611


class AriadneGraphQLModulesPlugin(Plugin):
    def get_method_hook(self, fullname: str):
        if "GraphQL" in fullname and fullname.endswith(".field"):
            return self.transform_graphql_object
        return None

    def transform_graphql_object(self, ctx: MethodContext):
        default_any_type = ctx.default_return_type

        default_type_arg = ctx.args[2]
        if default_type_arg:
            default_type = ctx.arg_types[2][0]
            default_arg = default_type_arg[0]

            # Fallback to default Any type if the field is required
            if not isinstance(default_arg, EllipsisExpr):
                if isinstance(default_type, Instance):
                    return default_type

        return default_any_type


def plugin(_):
    return AriadneGraphQLModulesPlugin
