from pygame.math import Vector2
from pygutils.timer import Timer

from src.sprites.entity import Entity
from src.sprites.player import Player


class Monster:
    def get_player_distance_direction(self) -> tuple[int, Vector2]:
        """Calculates the distance and direction between the current
        monster and the player.

        Returns
            tuple[int, Vector2]: A tuple containing the distance (int)
                and direction (Vector2) between the monster and the
                player.
        """
        distance = (self.player.pos - self.pos).magnitude()
        direction = Vector2(0, 0)

        if distance > 0:
            direction = (self.player.pos - self.pos).normalize()

        return distance, direction

    def face_player(self, distance: float, direction: Vector2) -> None:
        """Sets the status of the monster based on the distance and
        direction of the player.

        Args:
            distance (float): The distance between the player and the
                monster.
            direction (Vector2): The direction vector from the player
                to the monster.
        """
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
        """Move the monster towards the given direction if it is in
        walk radius.

        Args:
            distance (float): The distance between the monster and the
                player.
            direction (Vector2): The direction in which the monster
                should move.
        """
        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split("_")[0]
        else:
            self.direction = Vector2(0, 0)

    def check_death(self):
        """Check if the health of the character is equal to or below
        zero, and if so, call the kill() method.
        """
        if self.health <= 0:
            self.kill()


class Coffin(Entity, Monster):
    def __init__(self, position: tuple[int, int], player: Player, *groups) -> None:
        self.animation_speed = 15

        super().__init__(position, "graphics/monster/coffin", *groups)

        self.health = 5
        self.max_health = self.health

        self.speed = 100

        self.player = player
        self.notice_radius = 550
        self.walk_radius = 400
        self.attack_radius = 100

        self.damage_done = False

    def init_cooldowns(self) -> dict[str, Timer]:
        """Initialize the cooldowns for coffin actions.

        Returns:
            dict[str, Timer]: A dictionary mapping action names to
                Timer objects representing the cooldowns.
        """
        return {"attack": Timer(3000), "ivulnerable": Timer(300)}

    def attack(self, distance: float) -> None:
        """Attacks the target if it is within the attack radius and the
        attack cooldown is not active.

        Args:
            distance (float): The distance between the attacker and the
                target.
        """
        if distance <= self.attack_radius and not self.cooldowns["attack"].active:
            self.status = f"{self.status.split('_')[0]}_attack"
            self.attacking = True
            self.damage_done = False
            self.cooldowns["attack"].activate()

    def animate(self, dt: float, distance: float) -> None:
        """Animates the object based on the elapsed time and distance.

        Args:
            dt (float): The elapsed time since the last frame.
            distance (float): The distance between the object and the
                player.
        """
        super().animate(dt)

        if (
            int(self.current_animation.index) == 4
            and self.attacking
            and not self.damage_done
        ):
            if distance < self.attack_radius:
                self.player.damage()
                self.damage_done = True

    def update(self, dt: float) -> None:
        """Updates the enemy's state and behavior based on the elapsed
        time.

        Args:
            dt (float): The elapsed time since the last update.
        """
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
        self.animation_speed = 15

        super().__init__(position, "graphics/monster/cactus", *groups)

        self.speed = 90

        self.player = player
        self.notice_radius = 600
        self.walk_radius = 500
        self.attack_radius = 350

        self.bullet_shot = False

    def init_cooldowns(self) -> dict[str, Timer]:
        """Initialize the cooldowns for cactus actions.

        Returns:
            dict[str, Timer]: A dictionary mapping action names to
                Timer objects representing the cooldowns.
        """
        return {"attack": Timer(2000), "ivulnerable": Timer(300)}

    def shoot(self, distance: float) -> None:
        """Shoots at a given distance if the distance is within the
        attack radius and the attack cooldown is not active.

        Args:
            distance (float): The distance at which to shoot.
        """
        if distance <= self.attack_radius and not self.cooldowns["attack"].active:
            self.status = f"{self.status.split('_')[0]}_attack"
            self.attacking = True
            self.bullet_shot = False
            self.cooldowns["attack"].activate()

    def animate(self, dt, distance: float, direction: Vector2) -> None:
        """Animates the object based on the elapsed time and distance.

        Args:
            dt (float): The elapsed time since the last frame.
            distance (float): The distance between the object and the
                player.
        """
        super().animate(dt)

        if (
            int(self.current_animation.index) == 6
            and self.attacking
            and not self.bullet_shot
        ):
            if distance < self.attack_radius:
                bullet_pos = self.rect.center + direction * 80
                self.events.notify(
                    "cactus:attack", position=bullet_pos, direction=direction
                )

                self.bullet_shot = True

    def update(self, dt: float) -> None:
        """Updates the enemy's state and behavior based on the elapsed
        time.

        Args:
            dt (float): The elapsed time since the last update.
        """
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
