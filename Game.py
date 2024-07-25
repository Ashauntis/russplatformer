import pygame
from pygame import mixer
from pygame.locals import *

from os import path
import pickle

from config import *

from levelexit import LevelExit
from player import Player
from world import World
from coin import Coin
from button import Button


class Game:
    def __init__(self):

        pygame.font.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        mixer.init()
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.font_game_over = pygame.font.SysFont(
            font_game_over_face, font_game_over_size
        )
        self.font_score = pygame.font.SysFont(font_score_face, font_score_size)

        self.screen = pygame.display.set_mode(
            (screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED
        )
        pygame.display.set_caption("Platformer")

        self.game_over = 0
        self.main_menu = True
        self.level = start_level
        self.score = 0
        self.level_score = 0  # score for the current level

        # Load our images
        self.sun_img = pygame.image.load("assets/img/sun.png")
        self.bg_img = pygame.image.load("assets/img/sky.png")
        self.restart_img = pygame.image.load("assets/img/restart_btn.png")
        self.start_img = pygame.image.load("assets/img/start_btn.png")
        self.exit_img = pygame.image.load("assets/img/exit_btn.png")

        # Load our sounds
        pygame.mixer.music.load("assets/audio/music.wav")
        pygame.mixer.music.play(-1, 0.0, 5000)
        self.coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
        self.coin_fx.set_volume(0.5)

        # Dummy Coin for score
        self.coin_group = pygame.sprite.Group()
        self.coin_group.add(Coin(tile_size // 2, tile_size // 2 + 3))

        self.world = self.reset_level(self.level)
        self.player = Player(self, 100, screen_height - 130)

        # buttons
        self.restart_button = Button(
            self.screen,
            screen_width // 2 - 50,
            screen_height // 2 + 100,
            self.restart_img,
        )
        self.start_button = Button(
            self.screen, screen_width // 2 - 350, screen_height // 2, self.start_img
        )
        self.exit_button = Button(
            self.screen, screen_width // 2 + 150, screen_height // 2, self.exit_img
        )

    def reset_level(self, level) -> World:
        if path.exists(f"level_data/level{level}_data"):
            pickle_in = open(f"level_data/level{level}_data", "rb")
            print(f"Loading level {level}")
        else:
            pickle_in = open(f"level_data/level0_data", "rb")
            print(f"Failed to find data file for level {level}. Loading level 0.")
        world_data = pickle.load(pickle_in)
        world = World(self.screen, world_data)

        return world

    def update(self):
        self.clock.tick(self.fps)

        self.screen.blit(self.bg_img, (0, 0))
        self.screen.blit(self.sun_img, (100, 100))

        if self.main_menu:
            if self.exit_button.draw():
                return False
            if self.start_button.draw():
                self.main_menu = False
        else:
            self.world.draw()

            self.game_over = self.player.update(self.game_over)
            # normal game state
            if self.game_over == 0:
                if pygame.sprite.spritecollide(
                    self.player, self.world.coin_group, True
                ):
                    self.coin_fx.play()
                    self.level_score += 1
                self.draw_text(
                    "X " + str(self.score + self.level_score),
                    self.font_score,
                    white,
                    tile_size - 10,
                    10,
                )
                self.coin_group.draw(self.screen)
                self.world.coin_group.draw(self.screen)
                self.world.blob_group.update()
                self.world.blob_group.draw(self.screen)
                self.world.lava_group.draw(self.screen)
                self.world.exit_group.draw(self.screen)
                self.world.platform_group.update()
                self.world.platform_group.draw(self.screen)

            # Player has died
            if self.game_over == -1:
                self.draw_text(
                    "Game Over!",
                    self.font_game_over,
                    white,
                    screen_width // 2 - 275,
                    screen_height // 2 - 100,
                )
                if self.restart_button.draw():
                    self.world = self.reset_level(self.level)
                    self.player.reset()
                    self.level_score = 0
                    self.game_over = 0
            # Player has won!
            if self.game_over == 1:
                self.score += self.level_score
                self.level_score = 0
                if self.level >= max_level:
                    self.draw_text(
                        "You Win!",
                        self.font_game_over,
                        white,
                        screen_width // 2 - 240,
                        screen_height // 2 - 175,
                    )
                    self.draw_text(
                        f"Score: {self.score}",
                        self.font_game_over,
                        white,
                        screen_width // 2 - 215,
                        screen_height // 2 - 50,
                    )
                    if self.restart_button.draw():
                        self.level = 0
                        self.score = 0
                        self.world = self.reset_level(self.level)
                        self.player.reset()
                        self.game_over = 0
                else:
                    self.level += 1
                    self.world = self.reset_level(self.level)
                    self.player.reset()
                    self.game_over = 0
        self.draw_debug_outlines()

        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.main_menu:
                    return False
                else:
                    self.main_menu = True

        return True

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_grid(self):
        for line in range(0, int(screen_width / tile_size + 1)):
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (0, line * tile_size),
                (screen_width, line * tile_size),
            )
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (line * tile_size, 0),
                (line * tile_size, screen_height),
            )

    def draw_debug_outlines(self):
        if DEBUG:
            pygame.draw.rect(self.screen, (255, 255, 255), self.player.rect, 2)

            for tile in self.world.tile_list:
                pygame.draw.rect(self.screen, (255, 255, 255), tile[1], 2)

            draw_list = [
                self.world.blob_group,
                self.world.platform_group,
            ]

            for item in draw_list:
                for tile in item:
                    pygame.draw.rect(self.screen, (255, 255, 255), tile.rect, 2)
