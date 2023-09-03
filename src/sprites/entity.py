from abc import ABCMeta, abstractmethod
import os

from pygame.math import Vector2
from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.image import load as load_image
from pygame.mask import from_surface as mask_from_surface

from src.core.timer import Timer
from src.core.event_bus import bus


class Entity(Sprite, metaclass=ABCMeta):
    def __init__(self, position: tuple[int, int], assets_path: str, *groups) -> None:
        super().__init__(*groups)

        self.assets = self.import_assets(assets_path)
        self.status = "down_idle"
        self.previous_status = self.status
        self.animation_speed = 7
        self.frame_index = 0

        self.image = self.assets[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.6, -self.rect.height / 2)
        self.mask = mask_from_surface(self.image)

        self.pos = Vector2(self.rect.center)
        self.direction = Vector2(0, 0)
        self.speed = 200

        self.attacking = False
        self.cooldowns = self.init_cooldowns()
        self.health = 3

    def damage(self) -> None:
        self.health -= 1

    def import_assets(self, path: str) -> dict[str, list[Surface]]:
        animations = {}

        for root, dirs, files in os.walk(path):
            if not dirs:
                animations[root.split("/")[-1]] = [
                    load_image(f"{root}/{file}").convert_alpha()
                    for file in sorted(files, key=lambda f: int(f.split(".")[0]))
                ]

        return animations

    def move(self, dt: float, entity: str) -> None:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        bus.emit(
            f"{entity}:move", entity=self, axis="horizontal", direction=self.direction
        )

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery
        bus.emit(
            f"{entity}:move", entity=self, axis="vertical", direction=self.direction
        )

    def animate(self, dt) -> None:
        animations = self.assets[self.status]

        self.frame_index += self.animation_speed * dt

        if self.previous_status != self.status:
            self.previous_status = self.status
            self.frame_index = 0

        if self.attacking and self.frame_index >= len(animations):
            self.attacking = False

        self.image = animations[int(self.frame_index % len(animations))]
        self.mask = mask_from_surface(self.image)

    @abstractmethod
    def init_cooldowns(self) -> dict[str, Timer]:
        pass
