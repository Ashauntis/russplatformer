import pygame
from config import *


class Player:
    def __init__(self, game, x, y):
        self.game = game

        self.game_over_fx = pygame.mixer.Sound("assets/audio/game_over.wav")
        self.game_over_fx.set_volume(0.5)
        self.jump_fx = pygame.mixer.Sound("assets/audio/jump.wav")
        self.jump_fx.set_volume(0.5)

        self.reset(x, y)

    def reset(self, x=100, y=screen_height - 130):
        # Animations
        self.images_right = []
        self.images_left = []
        self.index = 0
        for num in range(1, 5):
            img = pygame.transform.scale(
                pygame.image.load(f"assets/img/guy{num}.png"), (40, 80)
            )
            self.images_right.append(img)
            self.images_left.append(
                pygame.transform.flip(img, flip_x=True, flip_y=False)
            )
        self.counter = 0
        self.image = self.images_right[self.index]
        self.dead_image = pygame.image.load("assets/img/ghost.png")
        self.height = self.image.get_height()
        self.width = self.image.get_width()

        # Location and movement
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.in_air = True
        self.direction = 0

    def update(self, game_over):
        # check if dead
        if game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # check if alive
        elif game_over == 0:
            walk_cooldown = 5

            dx = 0
            dy = 0

            col_thresh = 20

            # get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and not self.in_air:
                self.vel_y = -15
                self.jump_fx.play()
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                self.counter += 1
                self.direction = -1
                dx -= 5
            if key[pygame.K_RIGHT]:
                self.counter += 1
                self.direction = 1
                dx += 5
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Handle Animations
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Add our Gravity

            self.vel_y += 1
            # Add a maximum velocity
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collisions
            colliding_left = False
            colliding_right = False
            colliding_up = False
            colliding_down = False

            self.in_air = True
            for tile in self.game.world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    if dx > 0: #moving right
                        colliding_right = True
                        dx = self.rect.right - tile[1].left
                    else:
                        colliding_left = True
                        dx = self.rect.left - tile[1].right

                # check for collision in y direction
                if tile[1].colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    # Check if below the ground ie jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    # Check if above the ground ie falling
                    elif self.vel_y > 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
                        colliding_down = True

                    # Player is colliding in both directions 
                    else:
                        game_over = -1
                        self.game_over_fx.play()


            # check for collision with enemies
            if pygame.sprite.spritecollide(self, self.game.world.blob_group, False):
                game_over = -1
                self.game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, self.game.world.lava_group, False):
                game_over = -1
                self.game_over_fx.play()

            # check for collision with our exit
            if pygame.sprite.spritecollide(self, self.game.world.exit_group, False):
                game_over = 1

            # check for collision with platforms
            for platform in self.game.world.platform_group:
                # collision in the x direction
                if platform.rect.colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0

                # collision in the y direction
                if platform.rect.colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    # # check if we had a collision while on the moving platform
                    if colliding_down or colliding_up:
                        print("colliding_down or colliding_up with platform")
                        game_over = -1

                    # check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top

                    # otherwise we are above the platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:

                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0

                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        # draw our player
        self.game.screen.blit(self.image, self.rect)
        return game_over
