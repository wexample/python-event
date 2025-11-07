from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from wexample_event.dataclass.listener_record import EventCallback


class ListenerState:
    dispatcher: "EventDispatcherMixin | None"  # type: ignore[name-defined]
    bindings: List[tuple[str, "EventCallback"]]

    def __init__(self) -> None:
        self.dispatcher = None
        self.bindings = []
