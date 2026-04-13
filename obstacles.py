import pygame
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, FIELD_HEIGHT, FIELD_WIDTH

class Obstacle:
    def __init__(self):
        # Position et dimensions de l'obstacle en mm
        self.mm_x = 600
        self.mm_y = 2000   
        self.width_mm  = 1800
        self.height_mm = 400

    def _to_px(self, mm_x, mm_y):
        px_x = int(mm_x * FIELD_WIDTH  / TABLE_WIDTH_MM)
        px_y = int((TABLE_HEIGHT_MM - mm_y) * FIELD_HEIGHT / TABLE_HEIGHT_MM)
        return px_x, px_y

    def generate_obstacle(self):
        x, y = self._to_px(self.mm_x, self.mm_y)
        w = int(self.width_mm * FIELD_WIDTH  / TABLE_WIDTH_MM)
        h = int(self.height_mm * FIELD_HEIGHT / TABLE_HEIGHT_MM)
        return pygame.Rect(x, y, w, h)
    
    def draw(self, screen, color=(255, 80, 0)):
        rect = self.generate_obstacle()
        pygame.draw.rect(screen, color, rect)