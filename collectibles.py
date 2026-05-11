import pygame
import math
import random
from obstacles import Obstacle
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, FIELD_HEIGHT, FIELD_WIDTH

class Collectible(Obstacle):
    def __init__(self, mm_x=None, mm_y=None, mm_width=200, mm_height=100):
        super().__init__()
        #self.mm_x = random.randint(0, FIELD_WIDTH)
        #self.mm_y = random.randint(0, FIELD_HEIGHT)
        self.mm_x = 600 if mm_x is None else mm_x
        self.mm_y = 1400 if mm_y is None else mm_y
        self.mm_width = mm_width
        self.mm_height = mm_height
        self.mm_collect_radius = 50 
    
    def generate_collectible(self):
        x, y = self._to_px(self.mm_x + self.mm_width, self.mm_y)
        w = int(self.mm_width * FIELD_WIDTH  / TABLE_WIDTH_MM)
        h = int(self.mm_height * FIELD_HEIGHT / TABLE_HEIGHT_MM)
        return pygame.Rect(x, y, w, h)
    
    def midpoint(self):
        x1 = self.mm_x
        y1 = self.mm_y
        x2 = self.mm_x + self.mm_width
        y2 = self.mm_y - self.mm_height
        return (x2 + x1) / 2, (y2 + y1) / 2
    
    def generate_collect_circle(self):
        center_x, center_y = self.midpoint()
        radius_px = int(self.mm_collect_radius)
        center_px_x, center_px_y = self._to_px(center_x, center_y)
        return (center_px_x, center_px_y), radius_px
    
    def closest_point(self, robot_mm_x, robot_mm_y):
        #Override pour que prendre les coordonnées du collectible spécifiquement
        closest_x = max(self.mm_x, min(robot_mm_x, self.mm_x + self.mm_width))
        closest_y = max(self.mm_y, min(robot_mm_y, self.mm_y - self.mm_height))
        return closest_x, closest_y

    def has_collected(self, robot_mm_x, robot_mm_y):
        cx, cy = self.midpoint()
        distance = math.hypot(robot_mm_x - cx, robot_mm_y - cy)
        return distance < self.mm_collect_radius

    def draw(self, screen, color=(0, 34, 255)):
        rect = self.generate_collectible()
        pygame.draw.rect(screen, color, rect)
        circle_center, circle_radius = self.generate_collect_circle()
        pygame.draw.circle(screen, (255, 0, 0), circle_center, circle_radius, width=1)

class VerticalCollectible(Collectible):
    def __init__(self, mm_x=None, mm_y=None, mm_width=200, mm_height=100):
        super().__init__(mm_x, mm_y, mm_height, mm_width)
    
    def midpoint(self):
        x1 = self.mm_x
        y1 = self.mm_y
        x2 = self.mm_x + self.mm_width
        y2 = self.mm_y - self.mm_height
        return (x2 + x1) / 2, (y2 + y1) / 2