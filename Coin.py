import pygame
from config import tile_size


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(
            pygame.image.load("assets/img/coin.png"), (tile_size // 2, tile_size // 2)
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
