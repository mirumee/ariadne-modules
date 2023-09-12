import sys
from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True)
class DeferredType:
    path: str


def deferred(module_path: str) -> DeferredType:
    if not module_path.startswith("."):
        return DeferredType(module_path)

    frame = sys._getframe(2)
    if not frame:
        raise RuntimeError(
            "'deferred' can't be called outside of class's attribute's "
            "definition context."
        )

    # TODO: Support up a level traversal for multiple levels
    package = cast(str, frame.f_globals["__package__"])
    return DeferredType(f"{package}{module_path}")
