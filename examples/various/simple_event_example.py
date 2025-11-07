from __future__ import annotations

from wexample_event.common.listener import EventListenerMixin
from wexample_event.common.priority import EventPriority
from wexample_helpers.classes.example.example import Example


class SimpleEventExample(Example):
    def execute(self) -> None:
        print("=== Simple Event Listening Example ===\n")

        # Example 1: Basic event listening
        print("1. Basic Event Listening:")
        self._basic_listening()

        print("\n2. Multiple Listeners:")
        self._multiple_listeners()

        print("\n3. Priority-based Execution:")
        self._priority_listeners()

        print("\n4. Decorator-based Listeners:")
        self._decorator_listeners()

        print("\n5. Once Listeners:")
        self._once_listeners()

    def _basic_listening(self) -> None:
        """Simple event dispatcher with one listener."""

        from wexample_event.common.dispatcher import EventDispatcherMixin
        from wexample_event.dataclass.event import Event

        # Create a dispatcher
        class App(EventDispatcherMixin):
            pass

        app = App()

        # Define a listener function
        def on_user_action(event: Event) -> None:
            print(f"   Event received: {event.name}")
            if event.payload:
                print(f"   Payload: {event.payload}")

        # Register the listener
        app.add_event_listener("user.click", on_user_action)

        # Dispatch the event
        app.dispatch("user.click", payload={"button": "submit"})

    def _multiple_listeners(self) -> None:
        """Multiple listeners on the same event."""

        from wexample_event.common.dispatcher import EventDispatcherMixin
        from wexample_event.dataclass.event import Event

        class App(EventDispatcherMixin):
            pass

        app = App()

        # Multiple listeners for the same event
        def logger(event: Event) -> None:
            print(f"   [LOG] Event: {event.name}")

        def analytics(event: Event) -> None:
            print(f"   [ANALYTICS] Tracking: {event.name}")

        def notifier(event: Event) -> None:
            print(f"   [NOTIFY] User notified about: {event.name}")

        app.add_event_listener("user.signup", logger)
        app.add_event_listener("user.signup", analytics)
        app.add_event_listener("user.signup", notifier)

        # All listeners will be called
        app.dispatch("user.signup", payload={"email": "user@example.com"})

    def _priority_listeners(self) -> None:
        """Listeners with different priorities."""

        from wexample_event.common.dispatcher import EventDispatcherMixin
        from wexample_event.dataclass.event import Event

        class App(EventDispatcherMixin):
            pass

        app = App()

        def first(event: Event) -> None:
            print("   → First (HIGH priority)")

        def second(event: Event) -> None:
            print("   → Second (NORMAL priority)")

        def third(event: Event) -> None:
            print("   → Third (LOW priority)")

        # Add in random order, but they'll execute by priority
        app.add_event_listener("process", second, priority=EventPriority.NORMAL)
        app.add_event_listener("process", third, priority=EventPriority.LOW)
        app.add_event_listener("process", first, priority=EventPriority.HIGH)

        app.dispatch("process")

    def _decorator_listeners(self) -> None:
        """Using decorators for cleaner code."""

        from wexample_event.common.dispatcher import EventDispatcherMixin
        from wexample_event.dataclass.event import Event

        class App(EventDispatcherMixin):
            pass

        class UserHandler(EventListenerMixin):
            def __init__(self) -> None:
                self.login_count = 0

            @EventListenerMixin.on("user.login")
            def handle_login(self, event: Event) -> None:
                self.login_count += 1
                username = event.payload.get("username", "unknown")
                print(f"   User logged in: {username}")
                print(f"   Total logins: {self.login_count}")

            @EventListenerMixin.on("user.logout")
            def handle_logout(self, event: Event) -> None:
                username = event.payload.get("username", "unknown")
                print(f"   User logged out: {username}")

        app = App()
        handler = UserHandler()

        # Bind all decorated methods to the dispatcher
        handler.bind_to_dispatcher(app)

        # Dispatch events
        app.dispatch("user.login", payload={"username": "alice"})
        app.dispatch("user.login", payload={"username": "bob"})
        app.dispatch("user.logout", payload={"username": "alice"})

    def _once_listeners(self) -> None:
        """Listeners that run only once."""

        from wexample_event.common.dispatcher import EventDispatcherMixin
        from wexample_event.dataclass.event import Event

        class App(EventDispatcherMixin):
            pass

        app = App()

        def welcome_message(event: Event) -> None:
            print("   Welcome! This message appears only once.")

        def regular_message(event: Event) -> None:
            print("   This message appears every time.")

        # Add a one-time listener
        app.add_event_listener("app.start", welcome_message, once=True)
        app.add_event_listener("app.start", regular_message)

        print("   First dispatch:")
        app.dispatch("app.start")

        print("   Second dispatch:")
        app.dispatch("app.start")
