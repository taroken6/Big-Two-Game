import pygame
pygame.font.init()


class Button:
    def __init__(self, text, x, y, color, width, height):
        self.text = text
        self.x = x
        self.y = self.initial_y = y
        self.color = self.def_color = color
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_held_down = False
        self.key = None

    def draw(self, window):
        """
        Draws the button onto the window
        :param window:
        """
        pygame.gfxdraw.box(window, self.rect, self.color)
        font = pygame.font.SysFont('arial', 40)
        if self.color == (255,255,255):
            text = font.render(self.text, 1, (0,0,0))
        else:
            text = font.render(self.text, 1, (255,255,255))
        window.blit(text,
                    ((self.x + self.width/2 - text.get_width()/2), (self.y + self.height/2 - text.get_height()/2)))

    def lighten_button(self):
        """
        Visually "pops up" the button once the user lets go of the click button
        """
        self.color = self.def_color
        self.is_held_down = False

    def darken_button(self):
        """
        Visually "pushes down" the button when the user clicks on the button
        :return:
        """
        if not self.is_held_down:
            c1, c2, c3 = self.color
            if c1 > 50: c1 = c1 - 50
            if c2 > 50: c2 = c2 - 50
            if c3 > 50: c3 = c3 - 50
            self.color = (c1, c2, c3)
            self.is_held_down = True

    def click(self, pos):
        """
        Returns whether this button was clicked
        :param pos: Mouse position
        :return: True | False
        """
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False
