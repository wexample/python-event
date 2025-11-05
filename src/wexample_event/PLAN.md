Event package action plan

1. Define `Event` dataclass-like structure
   - Fields: `name: str`, `payload: Mapping[str, Any] | None`, `metadata: Mapping[str, Any] | None`, `timestamp: datetime`.
   - Provide helpers such as `with_update` to create derived events and `__repr__` for debugging.

2. Create `EventDispatcherMixin`
   - Maintains internal registry `listeners: dict[str, list[EventCallback]]`.
   - Public API: `add_event_listener(name, callback, *, once=False, priority=0)`, `remove_event_listener(name, callback)`, `dispatch_event(event)`.
   - Support synchronous callbacks and optional async dispatch via `dispatch_event_async`.

3. Add `EventListenerMixin`
   - Supplies convenience `on(event_name)` decorator to register methods as listeners when the instance is bound to a dispatcher.
   - Provides `bind_to_dispatcher(dispatcher)` and `unbind_from_dispatcher()` helpers.

4. Introduce `EventPriority` enum or constants to standardise priorities (e.g. `LOW`, `NORMAL`, `HIGH`).

5. Utility functions
   - `ensure_coroutine` to wrap sync callbacks for async dispatching.
   - Validation helpers for event names and listener signatures.

Example snippets

```python
from wexample_event import Event, EventDispatcherMixin

class Button(EventDispatcherMixin):
    def click(self) -> None:
        self.dispatch("button.click", payload={"source": self})
```

```python
button = Button()

def analytics_listener(event: Event) -> None:
    print("track", event.name)

button.add_event_listener("button.click", analytics_listener)
button.click()
```
