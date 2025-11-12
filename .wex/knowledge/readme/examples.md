# Examples

## Plugin System

```python
from wexample_event import Event, EventDispatcherMixin, EventListenerMixin

class Application(EventDispatcherMixin):
    def start(self) -> None:
        self.dispatch("app.startup")
        print("Application started")
    
    def stop(self) -> None:
        self.dispatch("app.shutdown")
        print("Application stopped")

class LoggingPlugin(EventListenerMixin):
    @EventListenerMixin.on("app.startup")
    def on_startup(self, event: Event) -> None:
        print("[LOG] Application is starting...")
    
    @EventListenerMixin.on("app.shutdown")
    def on_shutdown(self, event: Event) -> None:
        print("[LOG] Application is shutting down...")

class MetricsPlugin(EventListenerMixin):
    @EventListenerMixin.on("app.startup")
    def on_startup(self, event: Event) -> None:
        print("[METRICS] Recording startup time")

# Setup
app = Application()
logging_plugin = LoggingPlugin()
metrics_plugin = MetricsPlugin()

logging_plugin.bind_to_dispatcher(app)
metrics_plugin.bind_to_dispatcher(app)

# Run
app.start()
app.stop()
```

## State Change Notifications

```python
from wexample_event import Event, EventDispatcherMixin

class DataStore(EventDispatcherMixin):
    def __init__(self) -> None:
        self._data: dict = {}
    
    def set(self, key: str, value: any) -> None:
        old_value = self._data.get(key)
        self._data[key] = value
        
        self.dispatch(
            "data.changed",
            payload={"key": key, "old": old_value, "new": value}
        )
    
    def get(self, key: str) -> any:
        return self._data.get(key)

# Create store and add listeners
store = DataStore()

def on_data_changed(event: Event) -> None:
    payload = event.payload
    print(f"Data changed: {payload['key']} = {payload['new']}")

store.add_event_listener("data.changed", on_data_changed)

# Use the store
store.set("username", "alice")
store.set("username", "bob")
```

## Request/Response Pipeline

```python
from wexample_event import Event, EventDispatcherMixin, EventPriority

class RequestPipeline(EventDispatcherMixin):
    def process(self, request: dict) -> dict:
        # Create event with mutable response
        response = {"status": "pending", "data": request}
        
        self.dispatch(
            "request.process",
            payload={"request": request, "response": response}
        )
        
        return response

pipeline = RequestPipeline()

# Authentication middleware (high priority)
def authenticate(event: Event) -> None:
    response = event.payload["response"]
    request = event.payload["request"]
    
    if not request.get("auth_token"):
        response["status"] = "error"
        response["message"] = "Authentication required"
    else:
        response["authenticated"] = True

# Validation middleware (normal priority)
def validate(event: Event) -> None:
    response = event.payload["response"]
    if response["status"] == "error":
        return  # Skip if already errored
    
    request = event.payload["request"]
    if not request.get("data"):
        response["status"] = "error"
        response["message"] = "Data required"

# Processing (low priority)
def process_data(event: Event) -> None:
    response = event.payload["response"]
    if response["status"] == "error":
        return
    
    response["status"] = "success"
    response["processed"] = True

pipeline.add_event_listener("request.process", authenticate, priority=EventPriority.HIGH)
pipeline.add_event_listener("request.process", validate, priority=EventPriority.NORMAL)
pipeline.add_event_listener("request.process", process_data, priority=EventPriority.LOW)

# Process requests
result1 = pipeline.process({"auth_token": "abc", "data": {"value": 123}})
print(result1)  # Success

result2 = pipeline.process({"data": {"value": 456}})
print(result2)  # Error: Authentication required
```

## Event Inheritance

```python
from wexample_event import Event, EventDispatcherMixin, EventListenerMixin

class BaseListener(EventListenerMixin):
    @EventListenerMixin.on("base.event")
    def handle_base(self, event: Event) -> None:
        print("Base handler")

class ExtendedListener(BaseListener):
    @EventListenerMixin.on("extended.event")
    def handle_extended(self, event: Event) -> None:
        print("Extended handler")

dispatcher = EventDispatcherMixin()
listener = ExtendedListener()
listener.bind_to_dispatcher(dispatcher)

# Both base and extended events work
dispatcher.dispatch("base.event")      # Prints: Base handler
dispatcher.dispatch("extended.event")  # Prints: Extended handler
```

## Dynamic Event Names

```python
from wexample_event import Event, EventDispatcherMixin

class EventBus(EventDispatcherMixin):
    def emit(self, event_type: str, **data) -> None:
        self.dispatch(f"event.{event_type}", payload=data)

bus = EventBus()

# Add wildcard-style handlers
def handle_user_events(event: Event) -> None:
    print(f"User event: {event.name}")

bus.add_event_listener("event.user.login", handle_user_events)
bus.add_event_listener("event.user.logout", handle_user_events)

# Emit events
bus.emit("user.login", username="alice")
bus.emit("user.logout", username="alice")
```
