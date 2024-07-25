import pygame

class Button():
    def __init__(self, screen, x, y, image):
        self.screen = screen
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

        self.screen.blit(self.image, offset)

        # return true if our button was clicked
        return action
