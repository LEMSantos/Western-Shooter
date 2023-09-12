from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self.registered_events: dict[str, Callable] = {}

    def on(self, event_name: str) -> Callable:
        """Decorator that registers a function as a handler for a
        specific event.

        Args:
            event_name (str): The name of the event to handle.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable) -> Callable:
            self.registered_events[event_name] = func
            return func

        return decorator

    def emit(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event.

        Args:
            event_name (str): The name of the event to emit.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if event_name in self.registered_events:
            self.registered_events[event_name](*args, **kwargs)


bus = EventBus()
