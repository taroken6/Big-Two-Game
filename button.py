import pygame
pygame.font.init()

class Button:
    def __init__(self, text, x, y, color, width, height, is_card):
        self.text = text
        self.x = x
        self.y = self.initial_y = y
        self.color = self.def_color = color
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_card = is_card
        self.is_held_down = False
        self.key = None

    def draw(self, window):
        pygame.gfxdraw.box(window, self.rect, self.color)
        if not self.is_card:
            font = pygame.font.SysFont('arial', 40)
            if self.color == (255,255,255):
                text = font.render(self.text, 1, (0,0,0))
            else:
                text = font.render(self.text, 1, (255,255,255))
            window.blit(text,((self.x + self.width/2 - text.get_width()/2) , (self.y + self.height/2 - text.get_height()/2)))

    def set_key(self, key):
        self.key = key

    def get_key(self):
        return self.key

    def lighten_button(self):
        self.color = self.def_color
        self.is_held_down = False

    def darken_button(self):
        if not self.is_held_down:
            c1, c2, c3 = self.color
            if c1 > 50: c1 = c1 - 50
            if c2 > 50: c2 = c2 - 50
            if c3 > 50: c3 = c3 - 50
            self.color = (c1, c2, c3)
            self.is_held_down = True

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False

    def at_diff_pos(self):
        if self.y != self.initial_y:
            return True
        else:
            return False

    def reset_pos(self):
        self.y = self.initial_y

    def update_x(self, x):
        self.x = x

    def update_width(self, width, card_width):
        if width > card_width:
            self.width = card_width
        else:
            self.width = width
