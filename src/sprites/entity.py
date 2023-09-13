from abc import ABCMeta, abstractmethod
from math import sin
import os

from pygame.math import Vector2
from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.image import load as load_image
from pygame.time import get_ticks as get_clock_ticks
from pygame.mask import from_surface as mask_from_surface

from src.core.timer import Timer
from src.core.event_bus import bus

_surfaces_cache = {}


class Entity(Sprite, metaclass=ABCMeta):
    def __init__(self, position: tuple[int, int], assets_path: str, *groups) -> None:
        self.assets = self.import_assets(assets_path)
        self.status = "down_idle"
        self.previous_status = self.status
        self.animation_speed = 7
        self.frame_index = 0
        self.previous_frame_index = self.frame_index

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
        self.max_health = self.health

        super().__init__(*groups)

    def blink(self) -> None:
        """Toggles the image of the object between its original and a
        white version.
        """
        if self.cooldowns["ivulnerable"].active and self.weave_value():
            mask = mask_from_surface(self.image)

            white_surface = mask.to_surface()
            white_surface.set_colorkey("black")

            self.image = white_surface

    def weave_value(self) -> float:
        """Calculate a boolean value based on the current clock ticks.

        Returns:
            float: The calculated boolean value, which is the sine of
                the current clock ticks.
        """
        return sin(get_clock_ticks()) >= 0

    def damage(self) -> None:
        """Decreases the health of the entity by 1 if the "ivulnerable"
        cooldown is not active.
        """
        if not self.cooldowns["ivulnerable"].active:
            self.health -= 1
            self.cooldowns["ivulnerable"].activate()

            bus.emit("received:damage", entity=self)

    def import_assets(self, path: str) -> dict[str, list[Surface]]:
        """Imports assets from the specified path and returns a
        dictionary mapping animation names to lists of Surfaces.

        Args:
            path (str): The path to the directory containing the
                assets.

        Returns:
            dict[str, list[Surface]]: A dictionary mapping animation
                names to lists of Surfaces.
        """
        if path in _surfaces_cache:
            return _surfaces_cache[path]

        animations = {}

        for root, dirs, files in os.walk(path):
            if not dirs:
                animations[root.split("/")[-1]] = [
                    load_image(f"{root}/{file}").convert_alpha()
                    for file in sorted(files, key=lambda f: int(f.split(".")[0]))
                ]

        _surfaces_cache[path] = animations

        return animations

    def move(self, dt: float, entity: str) -> None:
        """Move the entity based on the given time delta.

        Args:
            dt (float): The time delta.
            entity (str): The name of the entity.
        """
        if self.direction.magnitude() == 0:
            return

        self.direction = self.direction.normalize()

        if self.direction.x != 0:
            self.pos.x += self.direction.x * self.speed * dt
            self.rect.centerx = round(self.pos.x)
            self.hitbox.centerx = self.rect.centerx

            bus.emit(
                f"{entity}:move",
                entity=self,
                axis="horizontal",
                direction=self.direction,
            )

        if self.direction.y != 0:
            self.pos.y += self.direction.y * self.speed * dt
            self.rect.centery = round(self.pos.y)
            self.hitbox.centery = self.rect.centery

            bus.emit(
                f"{entity}:move", entity=self, axis="vertical", direction=self.direction
            )

    def animate(self, dt: float) -> None:
        """Animate the object based on the given time interval.

        Args:
            dt (float): The time delta.
        """
        animations = self.assets[self.status]

        self.frame_index += self.animation_speed * dt
        new_frame_index = int(self.frame_index % len(animations))

        if self.previous_status != self.status:
            self.previous_status = self.status
            self.frame_index = 0
            new_frame_index = 0

        if self.attacking and self.frame_index >= len(animations):
            self.attacking = False

        if new_frame_index == self.previous_frame_index:
            return

        self.previous_frame_index = new_frame_index

        self.image = animations[new_frame_index]
        self.mask = mask_from_surface(self.image)

    @abstractmethod
    def init_cooldowns(self) -> dict[str, Timer]:
        """Initializes the cooldowns for the object.

        Returns:
            dict[str, Timer]: A dictionary where the keys are strings
                representing the names of the cooldowns, and the values
                are Timer objects representing the cooldown timers.
        """
        pass
