import pygame
from config import *

from game import Game

########## FUNCTIONS ###########


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_grid():
    for line in range(0, int(screen_width / tile_size + 1)):
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (0, line * tile_size),
            (screen_width, line * tile_size),
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (line * tile_size, 0),
            (line * tile_size, screen_height),
        )


def draw_debug_outlines():
    if DEBUG:
        pygame.draw.rect(screen, (255, 255, 255), player.rect, 2)
        for tile in world.tile_list:
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)
        for b in blob_group:
            pygame.draw.rect(screen, (255, 255, 255), b.rect, 2)


########## GAME LOGIC ##########

game = Game()
run = True

while run:
    # Returns true until a quit event is fired
    run = game.update()
    pygame.display.update()

pygame.quit()
