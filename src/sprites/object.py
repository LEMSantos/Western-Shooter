from pygame.sprite import Sprite
from pygame.surface import Surface


class Obstacle(Sprite):
    def __init__(self, position: tuple[int, int], surface: Surface, *groups) -> None:
        super().__init__(*groups)

        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)
