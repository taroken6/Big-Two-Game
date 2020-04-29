import pygame

class Debug:
    def draw_center(self, window, width, height):
        red = (255,0,0)

        rect = pygame.Rect(width / 2, height / 2, 5, 5)
        pygame.draw.rect(window, red, rect)