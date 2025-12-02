# Quickstart

## Basic Event Dispatching

```python
from wexample_event.dataclass.event import Event
from wexample_event.common.dispatcher import EventDispatcherMixin

# Create a dispatcher
class MyApp(EventDispatcherMixin):
    pass

app = MyApp()

# Add a listener
def on_user_login(event: Event) -> None:
    print(f"User logged in: {event.payload['username']}")

app.add_event_listener("user.login", on_user_login)

# Dispatch an event
app.dispatch("user.login", payload={"username": "john"})
```

## Using the Listener Mixin

```python
from wexample_event.dataclass.event import Event
from wexample_event.common.listener import EventListenerMixin
from wexample_event.common.dispatcher import EventDispatcherMixin

class MyDispatcher(EventDispatcherMixin):
    pass

class MyListener(EventListenerMixin):
    @EventListenerMixin.on("user.login")
    def handle_login(self, event: Event) -> None:
        print(f"Login handled: {event.payload['username']}")
    
    @EventListenerMixin.on("user.logout")
    def handle_logout(self, event: Event) -> None:
        print("User logged out")

# Setup
dispatcher = MyDispatcher()
listener = MyListener()
listener.bind_to_dispatcher(dispatcher)

# Dispatch events
dispatcher.dispatch("user.login", payload={"username": "jane"})
dispatcher.dispatch("user.logout")
```

## Async Events

```python
import asyncio
from wexample_event.dataclass.event import Event
from wexample_event.common.dispatcher import EventDispatcherMixin

class AsyncApp(EventDispatcherMixin):
    pass

app = AsyncApp()

async def async_handler(event: Event) -> None:
    await asyncio.sleep(0.1)
    print(f"Async handler: {event.name}")

app.add_event_listener("async.event", async_handler)

# Use dispatch_async for async handlers
await app.dispatch_async("async.event")
```

## Priority and Once

```python
from wexample_event.dataclass.event import Event
from wexample_event.common.priority import EventPriority
from wexample_event.common.dispatcher import EventDispatcherMixin

app = EventDispatcherMixin()

# High priority listener (runs first)
def high_priority(event: Event) -> None:
    print("High priority")

# Low priority listener (runs last)
def low_priority(event: Event) -> None:
    print("Low priority")

# One-time listener
def once_handler(event: Event) -> None:
    print("This runs only once")

app.add_event_listener("test", high_priority, priority=EventPriority.HIGH)
app.add_event_listener("test", low_priority, priority=EventPriority.LOW)
app.add_event_listener("test", once_handler, once=True)

app.dispatch("test")  # All three run
app.dispatch("test")  # Only high and low priority run
```
