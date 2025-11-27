# API Reference

## Core Classes

### Event

Immutable dataclass representing an event.

```python
@dataclass(frozen=True, slots=True)
class Event:
    name: str
    payload: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None
    source: Any | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

**Methods:**

- `with_update(**changes)` - Returns a copy with updated fields
- `derive(name=None, **changes)` - Creates a derived event, optionally with a new name

### EventDispatcherMixin

Mixin providing event dispatching capabilities.

**Methods:**

- `add_event_listener(name, callback, *, once=False, priority=DEFAULT_PRIORITY)` - Register a listener
- `remove_event_listener(name, callback)` - Remove a listener (returns bool)
- `clear_event_listeners(name=None)` - Clear listeners (all or for specific event)
- `has_event_listeners(name)` - Check if event has listeners
- `dispatch(event, *, payload=None, metadata=None, source=_UNSET)` - Dispatch synchronously
- `dispatch_async(event, *, payload=None, metadata=None, source=_UNSET)` - Dispatch asynchronously
- `dispatch_event(...)` - Alias for `dispatch`
- `dispatch_event_async(...)` - Alias for `dispatch_async`

### EventListenerMixin

Mixin for declarative event listeners using decorators.

**Class Method:**

- `@on(event_name, *, priority=DEFAULT_PRIORITY, once=False)` - Decorator to mark methods as listeners

**Methods:**

- `bind_to_dispatcher(dispatcher)` - Bind all decorated methods to a dispatcher
- `unbind_from_dispatcher()` - Unbind from current dispatcher
- `get_bound_dispatcher()` - Get the currently bound dispatcher

### EventPriority

Enum for common priority values.

```python
class EventPriority(IntEnum):
    LOW = -100
    NORMAL = 0
    HIGH = 100
```

**Constant:**

- `DEFAULT_PRIORITY = EventPriority.NORMAL`

## Type Aliases

```python
EventCallback = Callable[[Event], Awaitable[None] | None]
```

## Dataclasses

### ListenerRecord

Internal dataclass storing listener information.

```python
@dataclass(slots=True)
class ListenerRecord:
    callback: EventCallback
    once: bool
    priority: int
    order: int
```

### ListenerSpec

Internal dataclass for decorator metadata.

```python
@dataclass(frozen=True, slots=True)
class ListenerSpec:
    name: str
    priority: int
    once: bool
```

### ListenerState

Internal class managing listener binding state.

```python
class ListenerState:
    dispatcher: EventDispatcherMixin | None
    bindings: List[tuple[str, EventCallback]]
```

## Usage Patterns

### Synchronous Listener

```python
def my_listener(event: Event) -> None:
    print(event.name)
```

### Asynchronous Listener

```python
async def my_async_listener(event: Event) -> None:
    await some_async_operation()
```

### Decorator Pattern

```python
class MyListener(EventListenerMixin):
    @EventListenerMixin.on("event.name", priority=EventPriority.HIGH)
    def handle_event(self, event: Event) -> None:
        pass
```

### Custom Priority

```python
dispatcher.add_event_listener("event", callback, priority=50)
```

### Once Listener

```python
dispatcher.add_event_listener("event", callback, once=True)
```
