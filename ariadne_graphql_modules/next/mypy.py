from mypy.plugin import Plugin


class AriadneGraphQLModulesPlugin(Plugin):
    def get_type_analyze_hook(self, fullname: str):
        print(fullname)


def plugin(version: str):
    return AriadneGraphQLModulesPlugin
