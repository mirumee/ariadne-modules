import sys
from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True)
class DeferredTypeData:
    path: str


def deferred(module_path: str) -> DeferredTypeData:
    if not module_path.startswith("."):
        return DeferredTypeData(module_path)

    frame = _get_caller_frame()
    current_package = cast(str, frame.f_globals["__package__"])

    module_path_suffix = _resolve_module_path_suffix(module_path, current_package)

    return DeferredTypeData(module_path_suffix)


def _get_caller_frame():
    """Retrieve the caller's frame and ensure it's within a valid context."""
    frame = sys._getframe(2)  # pylint: disable=protected-access
    if not frame:
        raise RuntimeError(
            "'deferred' must be called within a class attribute definition context."
        )
    return frame


def _resolve_module_path_suffix(module_path: str, current_package: str) -> str:
    """Resolve the full module path by handling relative imports."""
    module_path_suffix = module_path[1:]  # Remove initial dot
    packages = current_package.split(".")

    while module_path_suffix.startswith(".") and packages:
        module_path_suffix = module_path_suffix[1:]  # Remove dot
        packages.pop()

        if not packages:
            raise ValueError(
                f"'{module_path}' points outside of the '{current_package}' package."
            )

    return (
        f"{'.'.join(packages)}.{module_path_suffix}" if packages else module_path_suffix
    )
