import pygame, random
import math as m

from pygame import *

pygame.init()

WINDOW_SIZE = (800, 480)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32) 
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

class surface_water_particle():
    k = 0.04 
    d = 0.08 
    def __init__(self, x, y):
        self.x_pos = x
        self.y_pos = y
        self.target_y = y
        self.velocity = 0

    def update(self):
        x = self.y_pos - self.target_y 
        a = -self.k * x - self.d * self.velocity

        self.y_pos += self.velocity
        self.velocity += a

class water():
    def __init__(self, x_start, x_end, y_start, y_end, segment_length):
        self.springs = []
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end - 10
        self.segment_length = segment_length
        for i in range(abs(x_end - x_start) // segment_length):
            self.springs.append(surface_water_particle(i * segment_length + x_start, y_end))

    def update(self, spread):
        passes = 4
        for i in range(len(self.springs)):
            self.springs[i].update()

        leftDeltas = [0] * len(self.springs)
        rightDeltas = [0] * len(self.springs)
        for p in range(passes):
            for i in range(0, len(self.springs) - 1):
                if i > 0:
                    leftDeltas[i] = spread * (self.springs[i].y_pos - self.springs[i - 1].y_pos)
                    self.springs[i - 1].velocity += leftDeltas[i]
                if i < len(self.springs) - 1:
                    rightDeltas[i] = spread * (self.springs[i].y_pos - self.springs[i + 1].y_pos)
                    self.springs[i + 1].velocity += rightDeltas[i]

            for i in range(0, len(self.springs) - 1):
                if i > 0:
                    self.springs[i - 1].y_pos += leftDeltas[i]
                if i < len(self.springs) - 1:
                    self.springs[i + 1].y_pos += rightDeltas[i]

    def splash(self, x_position, speed):
        index = int((x_position - self.x_start) / self.segment_length)
        if 0 <= index < len(self.springs):
            self.springs[index].velocity = speed

    def draw(self):
        water_surface = pygame.Surface((abs(self.x_start - self.x_end), abs(self.y_start - self.y_end))).convert_alpha()
        water_surface.fill((0, 0, 0, 0))
        water_surface.set_colorkey((0, 0, 0, 0))
        polygon_points = []
        polygon_points.append((self.x_start, self.y_start))
        for spring in range(len(self.springs)):
            polygon_points.append((water_test.springs[spring].x_pos, water_test.springs[spring].y_pos))
        polygon_points.append((water_test.springs[len(self.springs) - 1].x_pos, self.y_start))

        pygame.draw.polygon(water_surface, (0, 0, 255), polygon_points)

        for spring in range(0, len(self.springs) - 1):
            pygame.draw.line(screen, (0, 0, 255), 
                             (water_test.springs[spring].x_pos, water_test.springs[spring].y_pos),
                             (water_test.springs[spring + 1].x_pos, water_test.springs[spring + 1].y_pos), 2)

        water_surface.set_alpha(100)

        return water_surface
water_test = water(0, 900, 200, 200, 5)

while True:
    screen.fill((255, 255, 255))
    water_test.update(0.025)
    screen.blit(water_test.draw(), (0, 0))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            water_test.splash(mouse_x, 480-mouse_y)

    pygame.display.update()
    clock.tick(60)
