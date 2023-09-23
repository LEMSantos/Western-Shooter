from abc import ABCMeta, abstractmethod
from math import sin
import os

from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.image import load as load_image
from pygame.time import get_ticks as get_clock_ticks
from pygame.mask import from_surface as mask_from_surface
from pygutils.timer import Timer
from pygutils.animation import Animation
from pygutils.event import EventManager


class Entity(Sprite, metaclass=ABCMeta):
    def __init__(self, position: tuple[int, int], assets_path: str, *groups) -> None:
        self.events = EventManager()

        self.animation_speed = 10
        self.assets = self.import_assets(assets_path)
        self.status = "down_idle"
        self.previous_status = self.status
        self.current_animation = self.assets[self.status]
        self.previous_frame = self.current_animation.next()

        self.image = self.current_animation.next()
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

            self.events.notify("received:damage", entity=self)

    def disable_attack(self) -> None:
        self.attacking = False

    def import_assets(self, path: str) -> dict[str, Animation]:
        """Imports assets from the specified path and returns a
        dictionary mapping animation names to Animation objects.

        Args:
            path (str): The path to the directory containing the
                assets.

        Returns:
            dict[str, Animation]: A dictionary mapping animation
                names to Animation objects.
        """
        animations = {}

        for root, dirs, files in os.walk(path):
            if not dirs:
                name = root.split("/")[-1]
                is_attack_animation = name.endswith("_attack")

                animations[name] = Animation(
                    [
                        load_image(f"{root}/{file}").convert_alpha()
                        for file in sorted(files, key=lambda f: int(f.split(".")[0]))
                    ],
                    self.animation_speed,
                    loop=not is_attack_animation,
                    on_finish=None if not is_attack_animation else self.disable_attack,
                )

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

            self.events.notify(
                f"{entity}:move",
                entity=self,
                axis="horizontal",
                direction=self.direction,
            )

        if self.direction.y != 0:
            self.pos.y += self.direction.y * self.speed * dt
            self.rect.centery = round(self.pos.y)
            self.hitbox.centery = self.rect.centery

            self.events.notify(
                f"{entity}:move", entity=self, axis="vertical", direction=self.direction
            )

    def animate(self, dt: float) -> None:
        """Animate the object based on the given time interval.

        Args:
            dt (float): The time delta.
        """
        self.current_animation = self.assets[self.status]
        self.current_animation.update(dt)

        if self.previous_status != self.status:
            self.previous_status = self.status
            self.current_animation.reset()

        if self.current_animation.next() == self.previous_frame:
            return

        self.previous_frame = self.current_animation.next()

        self.image = self.current_animation.next()
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
