import pygame
from config import tile_size
from Exit import Exit
from Platform import Platform
from Coin import Coin
from Enemy import Enemy
from Lava import Lava


class World():
    def __init__(self, screen, data):
        self.screen = screen

        self.tile_list: list[tuple[pygame.surface.Surface, pygame.rect.Rect]] = []
        self.blob_group = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.lava_group = pygame.sprite.Group()
        self.exit_group = pygame.sprite.Group()


        # load images
        dirt_img = pygame.image.load('assets/img/dirt.png')
        grass_img = pygame.image.load('assets/img/grass.png')

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
                if tile == 3:
                    self.blob_group.add(Enemy(col_count * tile_size, row_count * tile_size + 15))                
                if tile == 4:
                    self.platform_group.add(Platform(col_count * tile_size, row_count * tile_size, 1, 0))
                if tile == 5:
                    self.platform_group.add(Platform(col_count * tile_size, row_count * tile_size, 0, 1))
                if tile == 6:
                    self.lava_group.add(Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2)))
                if tile == 7:
                    self.coin_group.add(Coin (col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2)))
                if tile == 8: 
                    tile = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    self.exit_group.add(tile)

                # increase our grid counters
                col_count += 1 
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            self.screen.blit(tile[0], tile[1])
