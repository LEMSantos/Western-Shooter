from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.mask import from_surface as mask_from_surface


class Obstacle(Sprite):
    def __init__(self, position: tuple[int, int], surface: Surface, *groups) -> None:
        super().__init__(*groups)

        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)


class Bullet(Sprite):
    def __init__(
        self, position: tuple[int, int], direction: Vector2, surface: Surface, *groups
    ) -> None:
        super().__init__(*groups)

        self.start_position = position

        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.mask = mask_from_surface(self.image)

        self.pos = Vector2(self.rect.center)
        self.direction = direction
        self.speed = 500

    def update(self, dt: float) -> None:
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.pos - self.start_position).magnitude() > 1500:
            self.kill()
