import pygame
from config import *

from game import Game

########## FUNCTIONS ###########


########## GAME LOGIC ##########

game = Game()
run = True

while run:
    # Returns true until a quit event is fired
    run = game.update()
    pygame.display.update()

pygame.quit()
