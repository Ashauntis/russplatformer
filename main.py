import pygame
from pygame.locals import *
import sys

pygame.init()

########## FUNCTIONS ###########

class World():
    def __init__(self, data):
        self.tile_list = []


        # load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data: 
            col_count = 0
            for tile in row: 

                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                # increase our grid counters
                col_count += 1 
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
    

def draw_grid():
    for line in range(0, 6):
        pygame.draw.line(screen, (255, 255, 255), (0, line*tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line*tile_size, 0), (line * tile_size, screen_height))

########## GAME LOGIC ##########

screen_width = 1000
screen_height = 1000

tile_size = 50

world_data = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [2, 2, 2, 2, 2],
]

world = World(world_data)
print(world.tile_list)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer")

# Load our images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')

run = True

while True: 

    screen.blit(bg_img, (0 ,0))
    screen.blit(sun_img, (100, 100))

    world.draw()

    draw_grid()

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    pygame.display.update()

pygame.quit()
