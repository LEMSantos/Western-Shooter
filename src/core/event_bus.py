from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self.registered_events: dict[str, Callable] = {}

    def on(self, event_name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.registered_events[event_name] = func
            return func

        return decorator

    def emit(self, event_name: str, *args, **kwargs) -> None:
        if event_name in self.registered_events:
            self.registered_events[event_name](*args, **kwargs)


bus = EventBus()
