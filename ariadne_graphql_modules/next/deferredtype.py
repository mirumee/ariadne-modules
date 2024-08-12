import sys
from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True)
class DeferredTypeData:
    path: str


def deferred(module_path: str) -> DeferredTypeData:
    if not module_path.startswith("."):
        return DeferredTypeData(module_path)

    frame = sys._getframe(2)  # pylint: disable=protected-access
    if not frame:
        raise RuntimeError(
            "'deferred' can't be called outside of class's attribute's "
            "definition context."
        )

    module_path_suffix = module_path[1:]  # Remove initial dot
    current_package = cast(str, frame.f_globals["__package__"])
    packages = current_package.split(".")

    while module_path_suffix.startswith(".") and packages:
        module_path_suffix = module_path_suffix[1:]  # Remove dot
        packages = packages[:-1]
        if not packages:
            raise ValueError(
                f"'{module_path}' points outside of the '{current_package}' package."
            )

    package = ".".join(packages)
    return DeferredTypeData(f"{package}.{module_path_suffix}")
