from pygame import SRCALPHA
from pygame.math import Vector2
from pygame.sprite import Group
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.draw import rect as draw_rect

from src.core.timer import Timer
from src.sprites.entity import Entity


class HealthBar(Sprite):
    def __init__(self, entity: Entity, *groups: list[Group]) -> None:
        super().__init__(*groups)

        self.entity = entity

        self.image = Surface((self.entity.rect.width // 2, 16), SRCALPHA)
        self.rect = self.image.get_rect(
            midbottom=Vector2(self.entity.rect.midtop) + Vector2(0, -15)
        )

        self.alive_timer = Timer(3000)
        self.alive_timer.activate()

    def keep_alive(self) -> None:
        self.alive_timer.deactivate()
        self.alive_timer.activate()

    def update(self) -> None:
        health_percent = self.entity.health / self.entity.max_health

        if (
            not self.alive_timer.active and health_percent > 0.5
        ) or health_percent == 0:
            self.kill()
            return

        draw_rect(
            surface=self.image,
            color=(0, 0, 0),
            rect=(0, 0, self.entity.rect.width // 2, 16),
            border_radius=5,
        )

        draw_rect(
            surface=self.image,
            color=(214, 75, 41),
            rect=(3, 3, self.entity.rect.width // 2 * health_percent - 6, 10),
            border_radius=3,
        )

        self.rect = self.image.get_rect(
            midbottom=Vector2(self.entity.rect.midtop) + Vector2(0, -15)
        )

        self.alive_timer.update()
