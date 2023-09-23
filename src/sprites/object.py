from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygutils.event import EventManager
from pygame.mask import from_surface as mask_from_surface


class Obstacle(Sprite):
    __slots__ = ("image", "rect", "hitbox")

    def __init__(self, position: tuple[int, int], surface: Surface, *groups) -> None:
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)

        super().__init__(*groups)


class Bullet(Sprite):
    __slots__ = (
        "pos",
        "mask",
        "rect",
        "image",
        "speed",
        "events",
        "direction",
        "start_position",
    )

    def __init__(
        self, position: tuple[int, int], direction: Vector2, surface: Surface, *groups
    ) -> None:
        self.events = EventManager()
        self.start_position = position

        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.mask = mask_from_surface(self.image)

        self.pos = Vector2(self.rect.center)
        self.direction = direction
        self.speed = 500

        super().__init__(*groups)

    def update(self, dt: float) -> None:
        """Update the position of the bullet based on the time passed.

        Args:
            dt (float): The time passed since the last update.
        """
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.pos - self.start_position).magnitude() > 700:
            self.kill()
            return

        self.events.notify("bullet:move", bullet=self)
