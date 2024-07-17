import pygame
from pygame.locals import *
import sys

pygame.init()
DEBUG = False
clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

tile_size = 50
game_over = 0

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Platformer")

########## FUNCTIONS ###########

class World():
    def __init__(self, data):
        self.reset(data)        

    def reset(self, data):
        blob_group.empty()
        lava_group.empty()
        self.tile_list: list[tuple[pygame.surface.Surface, pygame.rect.Rect]] = []

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
                if tile == 3:
                    blob_group.add(Enemy(col_count * tile_size, row_count * tile_size + 15))                
                if tile == 6:
                    lava_group.add(Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2)))

                # increase our grid counters
                col_count += 1 
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load('img/lava.png'), (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('img/blob.png')
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
            img = pygame.transform.scale(pygame.image.load(f'img/guy{num}.png'), (40, 80))
            self.images_right.append(img)
            self.images_left.append(pygame.transform.flip(img, flip_x=True, flip_y=False))
        self.counter = 0
        self.image = self.images_right[self.index]
        self.dead_image = pygame.image.load('img/ghost.png')
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

            # get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and not self.in_air:
                self.vel_y = -15
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

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        # draw our player
        screen.blit(self.image, self.rect)
        return game_over

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

world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Load our images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
world = World(world_data)
player = Player(100, screen_height - 130)

# buttons
restart_button = Button(screen_width // 2 -50, screen_height // 2 - 100, restart_img)

run = True

while run:

    clock.tick(fps)

    screen.blit(bg_img, (0 ,0))
    screen.blit(sun_img, (100, 100))

    world.draw()
    blob_group.update()
    blob_group.draw(screen)
    lava_group.draw(screen)

    game_over = player.update(game_over)
    if game_over:
        if restart_button.draw():
            player.reset(100, screen_height - 130)
            world.reset(world_data)
            game_over = 0

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False

    draw_debug_outlines()

    pygame.display.update()

pygame.quit()

