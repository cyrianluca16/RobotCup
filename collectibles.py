import pygame
import math
import random
from obstacles import Obstacle
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, FIELD_HEIGHT, FIELD_WIDTH

class Collectible(Obstacle):
    def __init__(self):
        super().__init__()
        self.mm_x = random.randint(0, FIELD_WIDTH)
        self.mm_y = random.randint(0, FIELD_HEIGHT)
        self.mm_width = 200
        self.mm_height = 100
        self.mm_collect_radius = 1
    
    def generate_collectible(self):
        x, y = self._to_px(self.mm_x, self.mm_y)
        w = int(self.mm_width * FIELD_WIDTH  / TABLE_WIDTH_MM)
        h = int(self.mm_height * FIELD_HEIGHT / TABLE_HEIGHT_MM)
        return pygame.Rect(x, y, w, h)
    
    def has_collected(self, robot_mm_x, robot_mm_y):
        distance = self.distance_to_robot(robot_mm_x, robot_mm_y)
        print(f"Distance to collectible: {distance} mm")
        return distance < self.mm_collect_radius

    def draw(self, screen, color=(0, 34, 255)):
        rect = self.generate_collectible()
        pygame.draw.rect(screen, color, rect)