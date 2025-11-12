# Introduction

`wexample-event` is a lightweight, thread-safe event dispatcher library for Python that implements the observer pattern. It provides a simple yet powerful way to decouple components in your application through event-driven communication.

## Key Features

- **Simple API** - Easy-to-use mixins for dispatching and listening to events
- **Type-safe** - Full type hints support for better IDE integration
- **Async Support** - Works with both synchronous and asynchronous event handlers
- **Priority System** - Control the execution order of event listeners
- **Thread-safe** - Built-in thread safety for concurrent applications
- **Decorator-based** - Clean syntax using Python decorators for event listeners
- **Zero Dependencies** - Only depends on `wexample-helpers`

## Use Cases

- **Application Events** - Coordinate actions across different parts of your application
- **Plugin Systems** - Allow plugins to react to application events
- **State Management** - Notify components when state changes occur
- **Logging & Monitoring** - Track application behavior through events
- **Decoupling** - Reduce tight coupling between components
