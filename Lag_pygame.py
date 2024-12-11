import pygame
import numpy as np
from pygame.locals import *
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
NX, NY = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

velocity_field = np.zeros((NY, NX, 2))
for i in range(NX):
    for j in range(NY):
        velocity_field[j, i] = [np.sin(j * 0.2), np.cos(i * 0.2)]

def calculate_pressure():
    pressure = np.zeros((NY, NX))
    for i in range(NX):
        for j in range(NY):
            vx, vy = velocity_field[j, i]
            pressure[j, i] = 1.0 / (1.0 + np.sqrt(vx**2 + vy**2))
    return pressure

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 4

    def update(self):
        grid_x = int(self.x // GRID_SIZE)
        grid_y = int(self.y // GRID_SIZE)
        if 0 <= grid_x < NX and 0 <= grid_y < NY:
            vx, vy = velocity_field[grid_y, grid_x]
            self.x += vx
            self.y += vy

        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface, pressure):
        grid_x = int(self.x // GRID_SIZE)
        grid_y = int(self.y // GRID_SIZE)
        if 0 <= grid_x < NX and 0 <= grid_y < NY:
            local_pressure = pressure[grid_y, grid_x]
            color_intensity = int(255 * local_pressure)
            color = (255 - color_intensity, color_intensity, 100)
        else:
            color = (255, 255, 255)

        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

particles = [Particle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(200)]

def update_velocity():
    global velocity_field
    for i in range(NX):
        for j in range(NY):
            velocity_field[j, i] += [0.01 * np.cos(j * 0.1), -0.01 * np.sin(i * 0.1)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    update_velocity()
    pressure = calculate_pressure()

    for particle in particles:
        particle.update()
        
    screen.fill((0, 0, 0))
    for particle in particles:
        particle.draw(screen, pressure)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
