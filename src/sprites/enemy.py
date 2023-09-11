from pygame.math import Vector2

from src.core.timer import Timer
from src.core.event_bus import bus
from src.sprites.entity import Entity
from src.sprites.player import Player


class Monster:
    def get_player_distance_direction(self) -> tuple[int, Vector2]:
        distance = (self.player.pos - self.pos).magnitude()
        direction = Vector2(0, 0)

        if distance > 0:
            direction = (self.player.pos - self.pos).normalize()

        return distance, direction

    def face_player(self, distance: float, direction: Vector2) -> None:
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

    def walk_to_player(self, distance: float, direction: Vector2) -> None:
        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split("_")[0]
        else:
            self.direction = Vector2(0, 0)

    def check_death(self):
        if self.health <= 0:
            self.kill()


class Coffin(Entity, Monster):
    def __init__(self, position: tuple[int, int], player: Player, *groups) -> None:
        super().__init__(position, "graphics/monster/coffin", *groups)

        self.speed = 100
        self.animation_speed = 15

        self.player = player
        self.notice_radius = 550
        self.walk_radius = 400
        self.attack_radius = 100

        self.damage_done = False

    def init_cooldowns(self) -> dict[str, Timer]:
        return {"attack": Timer(3000), "ivulnerable": Timer(300)}

    def attack(self, distance: float) -> None:
        if distance <= self.attack_radius and not self.cooldowns["attack"].active:
            self.status = f"{self.status.split('_')[0]}_attack"
            self.attacking = True
            self.damage_done = False
            self.cooldowns["attack"].activate()

    def animate(self, dt: float, distance: float) -> None:
        super().animate(dt)

        if int(self.frame_index) == 4 and self.attacking and not self.damage_done:
            if distance < self.attack_radius:
                self.player.damage()
                self.damage_done = True

    def update(self, dt: float) -> None:
        distance, direction = self.get_player_distance_direction()

        if not self.attacking:
            self.face_player(distance, direction)
            self.walk_to_player(distance, direction)
            self.attack(distance)
            self.move(dt, "coffin")

        for timer in self.cooldowns.values():
            timer.update()

        self.animate(dt, distance)
        self.check_death()
        self.blink()


class Cactus(Entity, Monster):
    def __init__(self, position: tuple[int, int], player: Player, *groups) -> None:
        super().__init__(position, "graphics/monster/cactus", *groups)

        self.speed = 90
        self.animation_speed = 15

        self.player = player
        self.notice_radius = 600
        self.walk_radius = 500
        self.attack_radius = 350

        self.bullet_shot = False

    def init_cooldowns(self) -> dict[str, Timer]:
        return {"attack": Timer(2000), "ivulnerable": Timer(300)}

    def shoot(self, distance: float) -> None:
        if distance <= self.attack_radius and not self.cooldowns["attack"].active:
            self.status = f"{self.status.split('_')[0]}_attack"
            self.attacking = True
            self.bullet_shot = False
            self.cooldowns["attack"].activate()

    def animate(self, dt, distance: float, direction: Vector2) -> None:
        super().animate(dt)

        if int(self.frame_index) == 6 and self.attacking and not self.bullet_shot:
            if distance < self.attack_radius:
                bullet_pos = self.rect.center + direction * 80
                bus.emit("cactus:attack", position=bullet_pos, direction=direction)

                self.bullet_shot = True

    def update(self, dt: float) -> None:
        distance, direction = self.get_player_distance_direction()

        if not self.attacking:
            self.face_player(distance, direction)
            self.walk_to_player(distance, direction)
            self.shoot(distance)
            self.move(dt, "cactus")

        for timer in self.cooldowns.values():
            timer.update()

        self.animate(dt, distance, direction)
        self.check_death()
        self.blink()
