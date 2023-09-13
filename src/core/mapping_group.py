from typing import Any
from collections import defaultdict

import numpy as np
from pygame.sprite import Group, Sprite


class MappingGroup(Group):
    def __init__(self, tile_size: int, *sprites) -> None:
        super().__init__(*sprites)

        self.tile_size = tile_size
        self.position_map = defaultdict(list)

    def add_internal(self, sprite: Any, layer: None = None) -> None:
        """Adds a sprite to the internal list of sprites and updates
        the position map.

        Args:
            sprite (Any): The sprite to be added.
            layer (None, optional): The layer to add the sprite to.
                Defaults to None.
        """
        if not self.has_internal(sprite):
            for pos in self._get_all_tiles_from_sprite(sprite):
                self.position_map[tuple(pos)].append(sprite)

        return super().add_internal(sprite, layer)

    def remove_internal(self, sprite: Any) -> None:
        """Remove the given sprite from the position map and from the
        internal list of the container.

        Args:
            sprite (Any): The sprite to be removed.
        """
        if self.has_internal(sprite):
            for pos in self._get_all_tiles_from_sprite(sprite):
                self.position_map[tuple(pos)].remove(sprite)

        return super().remove_internal(sprite)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update the position of the sprites on the game board.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        for sprite in self.sprites():
            old_sprite_pos = self._get_all_tiles_from_sprite(sprite)
            sprite.update(*args, **kwargs)
            new_sprite_pos = self._get_all_tiles_from_sprite(sprite)

            if tuple(new_sprite_pos[0]) != tuple(old_sprite_pos[0]):
                for old_pos in old_sprite_pos:
                    self.position_map[tuple(old_pos)].remove(sprite)

                for new_pos in new_sprite_pos:
                    self.position_map[tuple(new_pos)].append(sprite)

    def near_sprites(self, position: tuple[int, int]) -> list[Sprite]:
        """Returns a list of Sprite objects that are near the given
        position.

        Args:
            position (tuple[int, int]): The position to check for
                nearby sprites.

        Returns:
            list[Sprite]: A list of Sprite objects that are near the
                given position.
        """
        tile_pos = self._get_tile_position(*position)
        returned_sprites = []

        offsets = [
            (0, 0),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        for offset in offsets:
            near_pos = tile_pos[0] + offset[0], tile_pos[1] + offset[1]
            returned_sprites.extend(self.position_map[near_pos])

        return returned_sprites

    def _get_all_tiles_from_sprite(self, sprite: Any) -> list[tuple[int, int]]:
        """Retrieves all the tiles from a given sprite.

        Args:
            sprite (Any): The sprite from which to retrieve the tiles.

        Returns:
            list[tuple[int, int]]: A list of tuples representing the
                position of each tile.

        """
        top_sprite_tile = self._get_tile_position(*sprite.rect.topleft)
        tiles_range = (
            (sprite.rect.bottomright[0] - sprite.rect.topleft[0]) // self.tile_size,
            (sprite.rect.bottomright[1] - sprite.rect.topleft[1]) // self.tile_size,
        )

        y_pts = np.arange(
            top_sprite_tile[1], top_sprite_tile[1] + tiles_range[1] + 1, 1
        )
        x_pts = np.arange(
            top_sprite_tile[0], top_sprite_tile[0] + tiles_range[0] + 1, 1
        )

        X2D, Y2D = np.meshgrid(y_pts, x_pts)

        return np.column_stack((Y2D.ravel(), X2D.ravel()))

    def _get_tile_position(self, x: int, y: int) -> tuple[int, int]:
        """Returns the position of a tile based on the given x and y
        coordinates.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            tuple[int, int]: The position of the tile as a tuple of
                integers.
        """
        return x // self.tile_size, y // self.tile_size
