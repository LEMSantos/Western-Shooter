import sys

from pygame import quit as quit_game
from pygame.math import Vector2
from pygame.key import get_pressed as get_pressed_key
from pygame import K_LEFT, K_RIGHT, K_DOWN, K_UP, K_SPACE

from src.sprites.entity import Entity
from src.core.timer import Timer
from src.core.event_bus import bus


class Player(Entity):
    def __init__(self, position: tuple[int, int], *groups) -> None:
        super().__init__(position, "graphics/player", *groups)

        self.bullet_shot = False
        self.health = 10
        self.max_health = self.health

        self.keys_map = {
            K_UP: ("up", Vector2(0, -1)),
            K_RIGHT: ("right", Vector2(1, 0)),
            K_DOWN: ("down", Vector2(0, 1)),
            K_LEFT: ("left", Vector2(-1, 0)),
        }

    def init_cooldowns(self) -> dict[str, Timer]:
        """Initializes the cooldowns for the entity.

        Returns:
            dict[str, Timer]: A dictionary with the cooldown timers.
        """
        return {"attack": Timer(1000), "ivulnerable": Timer(300)}

    def move_input(self) -> None:
        """Moves the player based on the pressed keys.

        This function updates the `direction` attribute of the player
        based on the keys pressed by the user. It also updates the
        `status` attribute based on the keys pressed.
        """
        self.direction = Vector2(0, 0)
        self.status = f"{self.status.split('_')[0]}_idle"

        pressed_key = get_pressed_key()

        for key, (status, direction) in self.keys_map.items():
            if pressed_key[key]:
                self.direction += direction
                self.status = status

    def attack_input(self):
        """Process the input for attacking."""
        pressed_key = get_pressed_key()

        if pressed_key[K_SPACE]:
            self.shoot()

    def __get_shoot_direction(self) -> Vector2:
        """Retrieves the shoot direction based on the current status.

        Returns:
            Vector2: A vector representing the shoot direction.
        """
        direction = Vector2(0, 0)

        match self.status.split("_")[0]:
            case "up":
                direction = Vector2(0, -1)
            case "down":
                direction = Vector2(0, 1)
            case "left":
                direction = Vector2(-1, 0)
            case "right":
                direction = Vector2(1, 0)

        return direction

    def shoot(self) -> None:
        """Shoots a bullet if the attack cooldown is not active."""
        if not self.cooldowns["attack"].active:
            self.status = f"{self.status.split('_')[0]}_attack"
            self.cooldowns["attack"].activate()
            self.attacking = True
            self.bullet_shot = False

    def animate(self, dt: float) -> None:
        """Animates the object based on the given delta time.

        Args:
            dt (float): The time difference between frames.
        """
        super().animate(dt)

        if int(self.frame_index) == 2 and self.attacking and not self.bullet_shot:
            bullet_direction = self.__get_shoot_direction()
            bullet_pos = self.rect.center + bullet_direction * 80

            bus.emit("player:attack", position=bullet_pos, direction=bullet_direction)

            self.bullet_shot = True

    def check_death(self) -> None:
        """Check if the health of the character is less than or equal
        to 0. If so, quit the game and exit the program.
        """
        if self.health <= 0:
            quit_game()
            sys.exit()

    def update(self, dt: float) -> None:
        """Update the state of the object based on the given time
        increment.

        Args:
            dt (float): The time increment.
        """
        if not self.attacking:
            self.move_input()
            self.attack_input()
            self.move(dt, "player")

        for timer in self.cooldowns.values():
            timer.update()

        self.animate(dt)
        self.check_death()
        self.blink()
