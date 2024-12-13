import pygame
import numpy as np
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20 #오일러 방법은 격자를 중심으로 유체를 표현한다
NX, NY = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eulerian_Simulation")
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

def pressure_to_color(pressure):
    normalized = (pressure - pressure.min()) / (pressure.max() - pressure.min()) 
    return (normalized * 255).astype(int)

def add_pressure_at(x, y): #일정 위치에 압력을 주는 함수. 아래에서 마우스의 위치를 이용하여 이를 마우스 위치에 적용시킬 것
    grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE
    if 0 <= grid_x < NX and 0 <= grid_y < NY:
        radius = 5
        intensity = 0.5
        for i in range(max(0, grid_x - radius), min(NX, grid_x + radius)):
            for j in range(max(0, grid_y - radius), min(NY, grid_y + radius)):
                dx = i - grid_x
                dy = j - grid_y
                dist = np.sqrt(dx**2 + dy**2)
                if dist < radius:
                    factor = (radius - dist) / radius
                    velocity_field[j, i] += intensity * factor * np.array([dx, dy])

def update_velocity():
    global velocity_field
    for i in range(NX):
        for j in range(NY):
            velocity_field[j, i] += [0.01 * np.cos(j * 0.1), -0.01 * np.sin(i * 0.1)]

def draw_velocity_field():
    screen.fill((0, 0, 0))
    arrow_length = 15
    pressure = calculate_pressure()
    colors = pressure_to_color(pressure)

    for i in range(NX):
        for j in range(NY):
            x = i * GRID_SIZE + GRID_SIZE // 2
            y = j * GRID_SIZE + GRID_SIZE // 2
            vx, vy = velocity_field[j, i]
            
            mag = np.sqrt(vx**2 + vy**2)
            if mag > 0:
                vx, vy = vx / mag, vy / mag
                vx, vy = vx * arrow_length, vy * arrow_length
            
            color_intensity = colors[j, i]
            color = (255 - color_intensity, color_intensity, 100)

            pygame.draw.line(screen, color, (x, y), (x + vx, y + vy), 2)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                add_pressure_at(x, y)

    update_velocity()
    draw_velocity_field()

    pygame.display.flip()
    clock.tick(144)

pygame.quit()
