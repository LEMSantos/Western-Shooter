import os

from pygame.math import Vector2
from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.image import load as load_image
from pygame.key import get_pressed as get_pressed_key
from pygame.mask import from_surface as mask_from_surface
from pygame import K_LEFT, K_RIGHT, K_DOWN, K_UP, K_SPACE

from src.core.timer import Timer
from src.core.event_bus import bus


class Player(Sprite):
    def __init__(self, position: tuple[int, int], *groups) -> None:
        super().__init__(*groups)

        self.assets = self.import_assets()
        self.status = "down_idle"
        self.previous_status = self.status
        self.animation_speed = 10
        self.frame_index = 0

        self.image = self.assets[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.6, -self.rect.height / 2)
        self.mask = mask_from_surface(self.image)

        self.pos = Vector2(self.rect.center)
        self.direction = Vector2(0, 0)
        self.speed = 400

        self.attacking = False
        self.cooldowns = self.init_cooldowns()

    def import_assets(self) -> dict[str, list[Surface]]:
        path = "graphics/player"
        animations = {}

        for root, dirs, files in os.walk(path):
            if not dirs:
                animations[root.split("/")[-1]] = [
                    load_image(f"{root}/{file}").convert_alpha()
                    for file in sorted(files)
                ]

        return animations

    def init_cooldowns(self) -> dict[str, Timer]:
        return {"attack": Timer(1000)}

    def move_input(self) -> None:
        keys_map = {
            K_UP: ("up", Vector2(0, -1)),
            K_RIGHT: ("right", Vector2(1, 0)),
            K_DOWN: ("down", Vector2(0, 1)),
            K_LEFT: ("left", Vector2(-1, 0)),
        }

        self.direction = Vector2(0, 0)
        self.status = f"{self.status.split('_')[0]}_idle"

        pressed_key = get_pressed_key()

        for key, (status, direction) in keys_map.items():
            if pressed_key[key]:
                self.direction += direction
                self.status = status

    def attack_input(self):
        pressed_key = get_pressed_key()

        if pressed_key[K_SPACE]:
            self.shoot()

    def move(self, dt: float) -> None:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        bus.emit("player:move", axis="horizontal", direction=self.direction)

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery
        bus.emit("player:move", axis="vertical", direction=self.direction)

    def shoot(self) -> None:
        if not self.cooldowns["attack"].active:
            self.status = f"{self.status.split('_')[0]}_attack"
            self.cooldowns["attack"].activate()
            self.attacking = True
            bus.emit("player:attack", status=self.status)

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

    def update(self, dt: float) -> None:
        if not self.attacking:
            self.move_input()
            self.attack_input()
            self.move(dt)

        for timer in self.cooldowns.values():
            timer.update()

        self.animate(dt)
