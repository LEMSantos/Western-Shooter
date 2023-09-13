from operator import attrgetter
from typing import Iterable, Any, List

from pygame.rect import Rect
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.image import load as load_image
from pygame.sprite import AbstractGroup, Group

from src.sprites.player import Player
from settings import WINDOW_HEIGHT, WINDOW_WIDTH


class Camera(Group):
    def __init__(self, *sprites: Any | AbstractGroup | Iterable) -> None:
        super().__init__(*sprites)

        self.offset = Vector2(0, 0)
        self.bg_surf = load_image("graphics/other/bg.png").convert()

        self.half_width = WINDOW_WIDTH / 2
        self.half_height = WINDOW_HEIGHT / 2

    def custom_draw(self, surface: Surface, player: Player) -> None:
        """Draws the game screen on the provided surface, centered
        around the player.

        Args:
            surface (Surface): The surface on which to draw the game
                screen.
            player (Player): The player object that the screen should
                be centered around.
        """
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        surface.blit(self.bg_surf, -self.offset)

        screen_reference = Rect(self.offset, (WINDOW_WIDTH, WINDOW_HEIGHT))

        for sprite in self.sprites():
            if screen_reference.colliderect(sprite.rect):
                offset_pos = sprite.rect.topleft - self.offset
                surface.blit(sprite.image, offset_pos)

    def sprites(self) -> List:
        """Return a sorted list of sprites based on their y-coordinate.

        Returns:
            List: A list of sprites.
        """
        return sorted(super().sprites(), key=attrgetter("rect.centery"))
