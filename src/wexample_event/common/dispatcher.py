from __future__ import annotations

import inspect
import threading
from collections.abc import Mapping
from itertools import count
from typing import Any, ClassVar

from wexample_event.common.priority import DEFAULT_PRIORITY, EventPriority
from wexample_event.dataclass.event import Event
from wexample_event.dataclass.listener_record import EventCallback, ListenerRecord

# Hoisted at module level to avoid per-call attribute lookups on the inspect module.
_iscoroutinefunction = inspect.iscoroutinefunction
_isawaitable = inspect.isawaitable


def _listener_sort_key(item: ListenerRecord) -> tuple[int, int]:
    """Sort key for listener buckets: highest priority first, FIFO within priority."""
    return (-item.priority, item.order)


class EventDispatcherMixin:
    """Mixin providing a lightweight observer pattern implementation."""

    _LISTENERS_ATTR: ClassVar[str] = "_event_listeners"
    _LOCK_ATTR: ClassVar[str] = "_event_listener_lock"
    _ORDER_ATTR: ClassVar[str] = "_event_listener_order"
    _UNSET: ClassVar[object] = object()
    _enable_bubbling: ClassVar[bool] = False

    def add_event_listener(
        self,
        name: str,
        callback: EventCallback,
        *,
        once: bool = False,
        priority: int | EventPriority = DEFAULT_PRIORITY,
    ) -> None:
        """Register a callback for the given event name."""
        if not callable(callback):
            raise TypeError("callback must be callable")

        listeners, lock, order_seq = self._ensure_dispatcher_state()
        record = ListenerRecord(
            callback=callback,
            once=once,
            priority=int(priority),
            order=next(order_seq),
        )

        with lock:
            bucket = listeners.setdefault(name, [])
            bucket.append(record)
            bucket.sort(key=_listener_sort_key)

    def clear_event_listeners(self, name: str | None = None) -> None:
        """Remove all listeners. When name is provided, only that event is cleared."""
        listeners, lock, _ = self._ensure_dispatcher_state()

        with lock:
            if name is None:
                listeners.clear()
            else:
                listeners.pop(name, None)

    def dispatch(
        self,
        event: Event | str,
        *,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        source: Any | object = _UNSET,
    ) -> Event:
        """Synchronously dispatch an event to all registered listeners."""
        dispatched_event, records = self._snapshot_listeners(
            event, payload=payload, metadata=metadata, source=source
        )

        callbacks_to_remove: list[tuple[str, EventCallback]] = []
        for name, record in records:
            if _iscoroutinefunction(record.callback):
                raise RuntimeError(
                    "Listener is async; use dispatch_async for async listeners"
                )
            result = record.callback(dispatched_event)
            if _isawaitable(result):
                if hasattr(result, "close"):
                    result.close()
                raise RuntimeError(
                    "Listener returned an awaitable; use dispatch_async for async listeners"
                )
            if record.once:
                callbacks_to_remove.append((name, record.callback))

        for name, callback in callbacks_to_remove:
            self.remove_event_listener(name, callback)

        # Bubble event to parent if enabled
        if self._enable_bubbling:
            parent = self._get_bubbling_parent()
            if parent:
                parent.dispatch(dispatched_event)

        return dispatched_event

    async def dispatch_async(
        self,
        event: Event | str,
        *,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        source: Any | object = _UNSET,
    ) -> Event:
        """Asynchronously dispatch an event, awaiting coroutine listeners."""
        dispatched_event, records = self._snapshot_listeners(
            event, payload=payload, metadata=metadata, source=source
        )

        callbacks_to_remove: list[tuple[str, EventCallback]] = []
        for name, record in records:
            result = record.callback(dispatched_event)
            if _isawaitable(result):
                await result
            if record.once:
                callbacks_to_remove.append((name, record.callback))

        for name, callback in callbacks_to_remove:
            self.remove_event_listener(name, callback)

        # Bubble event to parent if enabled
        if self._enable_bubbling:
            parent = self._get_bubbling_parent()
            if parent:
                await parent.dispatch_async(dispatched_event)

        return dispatched_event

    def dispatch_event(
        self,
        event: Event | str,
        *,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        source: Any | object = _UNSET,
    ) -> Event:
        """Alias for dispatch to mirror other frameworks' APIs."""
        return self.dispatch(event, payload=payload, metadata=metadata, source=source)

    async def dispatch_event_async(
        self,
        event: Event | str,
        *,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        source: Any | object = _UNSET,
    ) -> Event:
        """Alias for dispatch_async for readability."""
        return await self.dispatch_async(
            event, payload=payload, metadata=metadata, source=source
        )

    def has_event_listeners(self, name: str) -> bool:
        # Short-circuit without initializing state if nothing has been registered yet.
        d = self.__dict__
        listeners = d.get(self._LISTENERS_ATTR)
        if not listeners:
            return False
        with d[self._LOCK_ATTR]:
            return bool(listeners.get(name))

    def remove_event_listener(
        self,
        name: str,
        callback: EventCallback,
    ) -> bool:
        """Remove a previously registered callback. Returns True if removed."""
        listeners, lock, _ = self._ensure_dispatcher_state()

        with lock:
            bucket = listeners.get(name)
            if not bucket:
                return False

            initial_length = len(bucket)
            bucket[:] = [
                record
                for record in bucket
                if not (record.callback is callback or record.callback == callback)
            ]
            new_length = len(bucket)
            if not new_length:
                listeners.pop(name, None)
            return new_length != initial_length

    def _coerce_event(
        self,
        event: Event | str,
        *,
        payload: Mapping[str, Any] | None,
        metadata: Mapping[str, Any] | None,
        source: Any | object,
    ) -> Event:
        if isinstance(event, Event):
            if payload is not None or metadata is not None or source is not self._UNSET:
                raise ValueError(
                    "Event instance cannot be combined with payload/metadata/source overrides"
                )
            return event

        resolved_source = self if source is self._UNSET else source
        return Event(
            name=event, payload=payload, metadata=metadata, source=resolved_source
        )

    def _ensure_dispatcher_state(
        self,
    ) -> tuple[dict[str, list[ListenerRecord]], threading.RLock, count]:
        # Use __dict__ directly for O(1) instance-dict access without MRO traversal.
        d = self.__dict__
        listeners_attr = self._LISTENERS_ATTR
        if listeners_attr not in d:
            d[listeners_attr] = {}
            d[self._LOCK_ATTR] = threading.RLock()
            d[self._ORDER_ATTR] = count()
        return d[listeners_attr], d[self._LOCK_ATTR], d[self._ORDER_ATTR]

    def _get_bubbling_parent(self) -> EventDispatcherMixin | None:
        """Override this method to return the parent dispatcher for event bubbling.

        Returns:
            The parent dispatcher to bubble events to, or None if no parent exists.

        Example:
            class FileNode(EventDispatcherMixin):
                _enable_bubbling = True

                def _get_bubbling_parent(self):
                    return self.parent  # or self.owner, self.container, etc.
        """
        return None

    def _snapshot_listeners(
        self,
        event: Event | str,
        *,
        payload: Mapping[str, Any] | None,
        metadata: Mapping[str, Any] | None,
        source: Any | object,
    ) -> tuple[Event, list[tuple[str, ListenerRecord]]]:
        listeners, lock, _ = self._ensure_dispatcher_state()
        dispatched_event = self._coerce_event(
            event, payload=payload, metadata=metadata, source=source
        )

        with lock:
            name = dispatched_event.name
            bucket = listeners.get(name, [])
            copied = [(name, record) for record in bucket]
        return dispatched_event, copied
