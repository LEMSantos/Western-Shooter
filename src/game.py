import sys

import pygame
from pytmx.util_pygame import load_pygame

from src.core.event_bus import bus
from src.core.camera import Camera
from src.sprites.entity import Entity
from src.sprites.player import Player
from src.sprites.enemy import Cactus, Coffin
from src.sprites.object import Bullet, Obstacle
from settings import (
    TILE_SIZE,
    GAME_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.groups = self.init_groups()
        self.map = self.init_map()

        self.bullet_surface = pygame.image.load(
            "graphics/other/particle.png"
        ).convert_alpha()

        self.register_events()

        self.sounds = self.init_sounds()
        self.sounds["music"].play(-1)

    def init_groups(self) -> dict[str, pygame.sprite.Group]:
        return {
            "all_sprites": Camera(),
            "obstacles": pygame.sprite.Group(),
            "bullets": pygame.sprite.Group(),
            "enemies": pygame.sprite.Group(),
        }

    def init_sounds(self) -> dict[str, pygame.mixer.Sound]:
        bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
        music_sound = pygame.mixer.Sound("sound/music.mp3")
        hit_sound = pygame.mixer.Sound("sound/hit.mp3")

        bullet_sound.set_volume(0.2)
        music_sound.set_volume(0.1)
        hit_sound.set_volume(0.2)

        return {
            "bullet": bullet_sound,
            "music": music_sound,
            "hit": hit_sound,
        }

    def __create_fence(self, tmx_map) -> None:
        for x, y, surface in tmx_map.get_layer_by_name("Fence").tiles():
            Obstacle(
                (x * TILE_SIZE, y * TILE_SIZE),
                surface,
                self.groups["all_sprites"],
                self.groups["obstacles"],
            )

    def __create_objects(self, tmx_map) -> None:
        for obj in tmx_map.get_layer_by_name("Objects"):
            Obstacle(
                (obj.x, obj.y),
                obj.image,
                self.groups["all_sprites"],
                self.groups["obstacles"],
            )

    def __create_entities(self, tmx_map) -> dict[str, Entity]:
        entities = {}
        enemy_map = {
            "Cactus": Cactus,
            "Coffin": Coffin,
        }

        for obj in tmx_map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                entities["player"] = Player(
                    (obj.x, obj.y),
                    self.groups["all_sprites"],
                )

            if obj.name in enemy_map:
                enemy_map[obj.name](
                    (obj.x, obj.y),
                    entities["player"],
                    self.groups["all_sprites"],
                    self.groups["enemies"],
                )

        return entities

    def init_map(self) -> dict[str, pygame.sprite.Sprite]:
        tmx_map = load_pygame("data/map.tmx")

        self.__create_fence(tmx_map)
        self.__create_objects(tmx_map)

        return self.__create_entities(tmx_map)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def register_events(self) -> None:
        bus.on("player:move")(self.collision_player_obstacles)
        bus.on("cactus:move")(self.collision_player_obstacles)
        bus.on("coffin:move")(self.collision_player_obstacles)

        bus.on("player:attack")(self.create_bullet)
        bus.on("cactus:attack")(self.create_bullet)

    def collision_player_obstacles(
        self, entity: Entity, axis: str, direction: pygame.math.Vector2
    ):
        for sprite in self.groups["obstacles"].sprites():
            if sprite.hitbox.colliderect(entity.hitbox):
                if axis == "horizontal":
                    if direction.x > 0:
                        entity.hitbox.right = sprite.hitbox.left
                    else:
                        entity.hitbox.left = sprite.hitbox.right
                else:
                    if direction.y < 0:
                        entity.hitbox.top = sprite.hitbox.bottom
                    else:
                        entity.hitbox.bottom = sprite.hitbox.top

                entity.pos = pygame.math.Vector2(entity.hitbox.center)
                entity.rect.center = entity.hitbox.center

    def bullet_collision(self) -> None:
        for bullet in self.groups["bullets"].sprites():
            for obstacle in self.groups["obstacles"].sprites():
                if pygame.sprite.collide_mask(bullet, obstacle):
                    bullet.kill()
                    continue

            for enemy in self.groups["enemies"].sprites():
                if pygame.sprite.collide_mask(bullet, enemy):
                    enemy.damage()
                    bullet.kill()
                    continue

            if pygame.sprite.collide_mask(bullet, self.map["player"]):
                self.map["player"].damage()
                self.sounds["hit"].play()
                bullet.kill()

    def create_bullet(
        self, position: tuple[int, int], direction: pygame.math.Vector2
    ) -> None:
        self.sounds["bullet"].play()
        Bullet(
            position,
            direction,
            self.bullet_surface,
            self.groups["all_sprites"],
            self.groups["bullets"],
        )

    def run(self) -> None:
        while True:
            self.handle_events()
            dt = self.clock.tick() / 1000

            self.groups["all_sprites"].update(dt)
            self.bullet_collision()

            self.screen.fill("black")
            self.groups["all_sprites"].custom_draw(self.screen, self.map["player"])

            pygame.display.update()
