import pygame
from pygame import mixer
from pygame.locals import *

from os import path
import pickle

from config import *

from player import Player
from world import World
from coin import Coin
from button import Button


class Game:
    def __init__(self):

        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        mixer.init()
        self.fps = 60
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(
            (screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED
        )
        pygame.display.set_caption("Platformer")

        self.game_over = 0
        self.main_menu = True
        self.level = 0
        self.score = 0

        # Load our images
        self.sun_img = pygame.image.load("assets/img/sun.png")
        self.bg_img = pygame.image.load("assets/img/sky.png")
        self.restart_img = pygame.image.load("assets/img/restart_btn.png")
        self.start_img = pygame.image.load("assets/img/start_btn.png")
        self.exit_img = pygame.image.load("assets/img/exit_btn.png")

        # Load our sounds
        pygame.mixer.music.load("assets/audio/music.wav")
        pygame.mixer.music.play(-1, 0.0, 5000)
        coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
        coin_fx.set_volume(0.5)

        self.world = self.reset_level(self.level)
        self.player = Player(self, 100, screen_height - 130)
        self.player.world = self.world

        # Dummy Coin for score
        self.coin_group = pygame.sprite.Group()
        self.coin_group.add(Coin(tile_size // 2, tile_size // 2 + 3))

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

        if main_menu:
            if self.exit_button.draw():
                run = False
            if self.start_button.draw():
                main_menu = False
        else:
            world.draw()

            game_over = self.player.update(game_over)
            # normal game state
            if game_over == 0:
                if pygame.sprite.spritecollide(self.player, self.coin_group, True):
                    self.coin_fx.play()
                    score += 1
                    print(f"Score: {score}")
                self.draw_text("X " + str(score), font_score, white, tile_size - 10, 10)
                self.coin_group.draw(self.screen)
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
                    font,
                    white,
                    screen_width // 2 - 275,
                    screen_height // 2 - 100,
                )
                if self.restart_button.draw():
                    self.world = self.reset_level(level)
                    self.player.reset(100, screen_height - 130)
                    self.score = 0
                    self.game_over = 0
            # Player has won!
            if self.game_over == 1:
                if self.level >= max_level:
                    self.draw_text(
                        "You Win!",
                        font,
                        white,
                        screen_width // 2 - 240,
                        screen_height // 2 - 175,
                    )
                    self.draw_text(
                        f"Score: {score}",
                        font,
                        white,
                        screen_width // 2 - 215,
                        screen_height // 2 - 50,
                    )
                    if self.restart_button.draw():
                        self.level = 0
                        self.score = 0
                        self.world = self.reset_level(self.level)
                        self.game_over = 0
                else:
                    self.level += 1
                    self.world = self.reset_level(self.level)
                    self.game_over = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.main_menu = True

        return True
