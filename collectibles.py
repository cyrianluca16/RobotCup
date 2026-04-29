import pygame
import math
import random
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, FIELD_HEIGHT, FIELD_WIDTH

class Collectible:
    def __init__(self):
        self.mm_x = random.randint(0, FIELD_WIDTH)
        self.mm_y = random.randint(0, FIELD_HEIGHT)
        self.mm_width = 200
        self.mm_height = 100
        self.mm_collect_radius = 100

    def _to_px(self, mm_x, mm_y):
        px_x = int(mm_x * FIELD_WIDTH  / TABLE_WIDTH_MM)
        px_y = int((TABLE_HEIGHT_MM - mm_y) * FIELD_HEIGHT / TABLE_HEIGHT_MM)
        return px_x, px_y
    
    def generate_collectible(self):
        x, y = self._to_px(self.mm_x, self.mm_y)
        w = int(self.mm_width * FIELD_WIDTH  / TABLE_WIDTH_MM)
        h = int(self.mm_height * FIELD_HEIGHT / TABLE_HEIGHT_MM)
        return pygame.Rect(x, y, w, h)
    
    def draw(self, screen, color=(80, 255, 80)):
        rect = self.generate_collectible()
        pygame.draw.rect(screen, color, rect)