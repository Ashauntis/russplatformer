import pygame
from config import *
from pygame import mixer
from pygame.locals import *
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
mixer.init()
DEBUG = False
clock = pygame.time.Clock()
fps = 60

game_over = 0
main_menu = True
level = 0
score = 0

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Platformer")

########## FUNCTIONS ###########

class World():
    def __init__(self, data):
        self.tile_list: list[tuple[pygame.surface.Surface, pygame.rect.Rect]] = []

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
                    blob_group.add(Enemy(col_count * tile_size, row_count * tile_size + 15))                
                if tile == 4:
                    platform_group.add(Platform(col_count * tile_size, row_count * tile_size, 1, 0))
                if tile == 5:
                    platform_group.add(Platform(col_count * tile_size, row_count * tile_size, 0, 1))
                if tile == 6:
                    lava_group.add(Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2)))
                if tile == 7:
                    coin_group.add(Coin (col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2)))
                if tile == 8: 
                    exit_group.add(Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2)))

                # increase our grid counters
                col_count += 1 
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load('assets/img/platform.png'), (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y 

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
 
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load('assets/img/lava.png'), (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load('assets/img/coin.png'), (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load('assets/img/exit.png'), (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
 
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.clicked = False

        self.last_pressed = False
        self.activating = False

    def draw(self):
        action = False
        # Get our mouse position
        pos = pygame.mouse.get_pos()
        in_button = self.rect.collidepoint(pos)
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # detect our mouse button down and up frame
        mouse_down = False
        mouse_up = False
        if mouse_pressed != self.last_pressed:
            mouse_down = mouse_pressed
            mouse_up = not mouse_pressed
        self.last_pressed = mouse_pressed

        if not in_button:
            # if the mouse leaves the button deactivate it
            self.activating = False
        else:

            # begin activating on a mouse button down inside the button
            if mouse_down:
                self.activating = True

            # confirm activation on a mouse button up inside the button
            if mouse_up and self.activating:
                action = True
                self.activating = False    

        # offset button for float/pending activation
        offset = self.rect.copy()
        if self.activating:
            # draw our button indented while activating
            offset.x += 3
            offset.y += 3
        else:
            # draw the mouse hover outdent while hovered
            if in_button:    
                offset.x -= 2
                offset.y -= 2

        screen.blit(self.image, offset)

        # return true if our button was clicked
        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)
    
    def reset(self, x, y):
        # Animations
        self.images_right = []
        self.images_left = []
        self.index = 0 
        for num in range(1, 5):
            img = pygame.transform.scale(pygame.image.load(f'assets/img/guy{num}.png'), (40, 80))
            self.images_right.append(img)
            self.images_left.append(pygame.transform.flip(img, flip_x=True, flip_y=False))
        self.counter = 0
        self.image = self.images_right[self.index]
        self.dead_image = pygame.image.load('assets/img/ghost.png')
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
                jump_fx.play()
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
                if self.index>= len(self.images_right):
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
            self.in_air = True
            for tile in world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below the ground ie jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y > 0: 
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # check for collision with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # check for collision with our exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
                
            # check for collision with platforms
            for platform in platform_group:
                # collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                
                # collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below platform

                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top

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
        screen.blit(self.image, self.rect)
        return game_over


def reset_level(level) -> World:  
    
    player.reset(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    coin_group.empty()
    
    if path.exists(f'level_data/level{level}_data'):
        pickle_in = open(f'level_data/level{level}_data', 'rb')
        print(f'Loading level {level}')
    else:
        pickle_in = open(f'level_data/level0_data', 'rb')
        print(f'Failed to find data file for level {level}. Loading level 0.')
    world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_grid():
    for line in range(0, int(screen_width/tile_size + 1)):
        pygame.draw.line(screen, (255, 255, 255), (0, line*tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line*tile_size, 0), (line * tile_size, screen_height))

def draw_debug_outlines():
    if DEBUG:
        pygame.draw.rect(screen, (255, 255, 255), player.rect, 2)
        for tile in world.tile_list:
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)
        for b in blob_group:
            pygame.draw.rect(screen, (255, 255, 255), b.rect, 2)


########## GAME LOGIC ##########

# Load our images
sun_img = pygame.image.load('assets/img/sun.png')
bg_img = pygame.image.load('assets/img/sky.png')
restart_img = pygame.image.load('assets/img/restart_btn.png')
start_img = pygame.image.load('assets/img/start_btn.png')
exit_img = pygame.image.load('assets/img/exit_btn.png')

# Load our sounds
pygame.mixer.music.load('assets/audio/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('assets/audio/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('assets/audio/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('assets/audio/game_over.wav')
game_over_fx.set_volume(0.5)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

player = Player(100, screen_height - 130)
world = reset_level(level)

# Dummy Coin for score
coin_group.add(Coin(tile_size // 2, tile_size // 2 + 3))

# buttons
restart_button = Button(screen_width // 2 -50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True

while run:

    clock.tick(fps)

    screen.blit(bg_img, (0 ,0))
    screen.blit(sun_img, (100, 100))

    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        game_over = player.update(game_over)
        # normal game state
        if game_over == 0:
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_fx.play()
                score += 1
                print(f'Score: {score}')
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)
            coin_group.draw(screen)
            blob_group.update()
            blob_group.draw(screen)
            lava_group.draw(screen)
            exit_group.draw(screen)
            platform_group.update()
            platform_group.draw(screen)

        # Player has died
        if game_over == -1:
            draw_text('Game Over!', font, white, screen_width // 2 - 275, screen_height // 2 - 100)
            if restart_button.draw():
                world = reset_level(level)
                score = 0
                game_over = 0
        # Player has won!
        if game_over == 1:
            if level >= max_level:
                draw_text('You Win!', font, white, screen_width // 2 - 240, screen_height // 2 - 175)
                draw_text(f'Score: {score}', font, white, screen_width // 2 - 215, screen_height // 2 - 50)
                if restart_button.draw():
                    level = 0
                    score = 0
                    world = reset_level(level)
                    game_over = 0
            else: 
                level += 1
                world = reset_level(level)
                game_over = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            main_menu = True

    draw_debug_outlines()

    pygame.display.update()

pygame.quit()

