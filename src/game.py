import sys

import pygame
from pytmx.util_pygame import load_pygame
from pygutils.camera import TopDownCamera

from src.sprites.entity import Entity
from src.sprites.player import Player
from src.sprites.enemy import Cactus, Coffin
from src.sprites.health_bar import HealthBar
from src.sprites.object import Bullet, Obstacle
from src.core.mapping_group import MappingGroup
from settings import (
    FRAME_RATE_LIMITER,
    TILE_SIZE,
    GAME_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class Game:
    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()

        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        self.bg_surf = pygame.image.load("graphics/other/bg.png").convert()

        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.groups = self.init_groups()
        self.map = self.init_map()

        self.bullet_surface = pygame.image.load(
            "graphics/other/particle.png"
        ).convert_alpha()

        self.sounds = self.init_sounds()
        self.sounds["music"].play(-1)

        self.health_bars = {}

    def init_groups(self) -> dict[str, pygame.sprite.Group]:
        return {
            "all_sprites": TopDownCamera(self.bg_surf),
            "obstacles": MappingGroup(TILE_SIZE * 2),
            "bullets": pygame.sprite.Group(),
            "enemies": MappingGroup(TILE_SIZE * 2),
            "health_bar": pygame.sprite.Group(),
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
                player = Player((obj.x, obj.y), self.groups["all_sprites"])
                player.events.subscribe("player:move", self)
                player.events.subscribe("player:attack", self)
                player.events.subscribe("received:damage", self)

                entities["player"] = player

            if obj.name in enemy_map:
                groups = [self.groups["all_sprites"], self.groups["enemies"]]
                enemy_name = obj.name.lower()

                enemy = enemy_map[obj.name]((obj.x, obj.y), player, groups)
                enemy.events.subscribe(f"{enemy_name}:move", self)
                enemy.events.subscribe("received:damage", self)

                if enemy_name == "cactus":
                    enemy.events.subscribe("cactus:attack", self)

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

    def collision_entity_obstacles(
        self, entity: Entity, axis: str, direction: pygame.math.Vector2
    ):
        for sprite in self.groups["obstacles"].near_sprites(entity.hitbox.center):
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

    def bullet_collision(self, bullet: Bullet) -> None:
        if pygame.sprite.collide_mask(bullet, self.map["player"]):
            self.map["player"].damage()
            self.sounds["hit"].play()
            bullet.kill()
            return

        for enemy in self.groups["enemies"].near_sprites(bullet.rect.center):
            if pygame.sprite.collide_mask(bullet, enemy):
                enemy.damage()
                self.sounds["hit"].play()
                bullet.kill()
                return

        for obstacle in self.groups["obstacles"].near_sprites(bullet.rect.center):
            if bullet.rect.colliderect(obstacle.hitbox):
                bullet.kill()
                break

    def create_bullet(
        self, position: tuple[int, int], direction: pygame.math.Vector2
    ) -> None:
        self.sounds["bullet"].play()
        bullet = Bullet(
            position,
            direction,
            self.bullet_surface,
            self.groups["all_sprites"],
            self.groups["bullets"],
        )
        bullet.events.subscribe("bullet:move", self)

    def create_health_bar(self, entity: Entity) -> None:
        if entity in self.health_bars and self.health_bars[entity].alive():
            self.health_bars[entity].keep_alive()
            return

        self.health_bars[entity] = HealthBar(
            entity, self.groups["health_bar"], self.groups["all_sprites"]
        )

    def render_fps(self):
        fps = str(round(self.clock.get_fps(), 2))
        fps_t = self.font.render(f"FPS: {fps}", 1, pygame.Color("RED"))
        self.screen.blit(fps_t, (10, 10))

    def notify(self, event: str, *args, **kwargs) -> None:
        match event.split(":"):
            case ["bullet", "move"]:
                action = self.bullet_collision
            case [_, "move"]:
                action = self.collision_entity_obstacles
            case [_, "attack"]:
                action = self.create_bullet
            case ["received", "damage"]:
                action = self.create_health_bar
            case _:
                return

        action(*args, **kwargs)

    def run(self) -> None:
        while True:
            self.handle_events()
            dt = self.clock.tick(FRAME_RATE_LIMITER) / 1000

            self.groups["enemies"].update(dt)
            self.map["player"].update(dt)
            self.groups["bullets"].update(dt)
            self.groups["health_bar"].update()

            rects_to_update = self.groups["all_sprites"].draw(
                surface=self.screen,
                target=self.map["player"],
            )

            self.render_fps()

            pygame.display.update(rects_to_update)
