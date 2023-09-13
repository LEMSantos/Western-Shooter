import pygame


class Timer:
    def __init__(self, duration: int, func=None):
        self.duration = duration
        self.func = func

        self.start_time = 0
        self.active = False

    def activate(self) -> None:
        """Activates the timer."""
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self) -> None:
        """Deactivates the timer."""
        self.active = False
        self.start_time = 0

    def update(self) -> None:
        """Update the state of the timer.

        This function is called to update the state of the timer. It
        checks if the duration has passed since the start time and if
        so, it executes the given function (if any) and deactivates the
        timer.
        """
        current_time = pygame.time.get_ticks()

        if (current_time - self.start_time) >= self.duration:
            if self.func and self.start_time != 0:
                self.func()

            self.deactivate()
