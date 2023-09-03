from operator import attrgetter
from typing import Iterable, Any

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

    def custom_draw(self, surface: Surface, player: Player) -> None:
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        surface.blit(self.bg_surf, -self.offset)

        for sprite in sorted(self.sprites(), key=attrgetter("rect.centery")):
            offset_pos = sprite.rect.topleft - self.offset
            surface.blit(sprite.image, offset_pos)
