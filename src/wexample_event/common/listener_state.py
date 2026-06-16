from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_event.common.dispatcher import EventDispatcherMixin
    from wexample_event.dataclass.listener_record import EventCallback


class ListenerState:
    # `dispatcher` is read/written before `bindings` in every hot path; list it
    # first so CPython places it in the earlier slot offset for better cache locality.
    __slots__ = ("dispatcher", "bindings")
    dispatcher: EventDispatcherMixin | None
    bindings: list[tuple[str, EventCallback]]

    def __init__(self) -> None:
        self.dispatcher = None
        self.bindings = []
