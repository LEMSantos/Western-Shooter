from pygame.math import Vector2

from src.core.timer import Timer
from src.sprites.entity import Entity
from src.sprites.player import Player


class Monster:
    def get_player_distance_direction(self) -> tuple[int, Vector2]:
        distance = (self.player.pos - self.pos).magnitude()
        direction = Vector2(0, 0)

        if distance > 0:
            direction = (self.player.pos - self.pos).normalize()

        return distance, direction

    def face_player(self) -> None:
        distance, direction = self.get_player_distance_direction()

        if distance < self.notice_radius:
            if -0.5 < direction.y < 0.5:
                if direction.x < 0:
                    self.status = "left_idle"
                elif direction.x > 0:
                    self.status = "right_idle"
            else:
                if direction.y < 0:
                    self.status = "up_idle"
                elif direction.y > 0:
                    self.status = "down_idle"

    def walk_to_player(self) -> None:
        distance, direction = self.get_player_distance_direction()

        self.direction = Vector2(0, 0)

        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split("_")[0]


class Coffin(Entity, Monster):
    def __init__(self, position: tuple[int, int], player: Player, *groups) -> None:
        super().__init__(position, "graphics/monster/coffin", *groups)

        self.speed = 100
        self.animation_speed = 15

        self.player = player
        self.notice_radius = 550
        self.walk_radius = 400
        self.attack_radius = 100

    def init_cooldowns(self) -> dict[str, Timer]:
        return {"attack": Timer(1000)}

    def update(self, dt: float) -> None:
        if not self.attacking:
            self.face_player()
            self.walk_to_player()
            self.move(dt, "coffin")

        for timer in self.cooldowns.values():
            timer.update()

        self.animate(dt)


class Cactus(Entity, Monster):
    def __init__(self, position: tuple[int, int], player: Player, *groups) -> None:
        super().__init__(position, "graphics/monster/cactus", *groups)

        self.speed = 100
        self.animation_speed = 15

        self.player = player
        self.notice_radius = 600
        self.walk_radius = 500
        self.attack_radius = 350

    def init_cooldowns(self) -> dict[str, Timer]:
        return {"attack": Timer(2000)}

    def update(self, dt: float) -> None:
        if not self.attacking:
            self.face_player()
            self.walk_to_player()
            self.move(dt, "cactus")

        for timer in self.cooldowns.values():
            timer.update()

        self.animate(dt)
