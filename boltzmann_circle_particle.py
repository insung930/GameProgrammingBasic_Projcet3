import pygame
import numpy as np

class LBMFluidSimulation:
    def __init__(self, width, height, tau):
        self.width = width
        self.height = height
        self.tau = tau 

        self.velocities = np.array([
            [0, 0], [1, 0], [0, 1], [-1, 0], [0, -1],
            [1, 1], [-1, 1], [-1, -1], [1, -1]
        ])
        self.weights = np.array([4/9] + [1/9]*4 + [1/36]*4)

        self.f = np.ones((9, height, width)) * (1/9)
        self.f_eq = np.zeros_like(self.f)

        self.rho = np.ones((height, width))
        self.u = np.zeros((2, height, width))

    def equilibrium(self):
        u_sq = self.u[0]**2 + self.u[1]**2
        for i in range(9):
            cu = (self.velocities[i, 0] * self.u[0] +
                  self.velocities[i, 1] * self.u[1])
            self.f_eq[i] = self.weights[i] * self.rho * (
                1 + 3*cu + 4.5*cu**2 - 1.5*u_sq
            )

    def collision(self):
        self.equilibrium()
        self.f += -(1 / self.tau) * (self.f - self.f_eq)

    def streaming(self):
        for i, (cx, cy) in enumerate(self.velocities):
            self.f[i] = np.roll(self.f[i], shift=cx, axis=1)  
            self.f[i] = np.roll(self.f[i], shift=cy, axis=0)  

    def macroscopic(self):
        self.rho = np.sum(self.f, axis=0) 
        self.u[0] = np.sum(self.f * self.velocities[:, 0, None, None], axis=0) / self.rho
        self.u[1] = np.sum(self.f * self.velocities[:, 1, None, None], axis=0) / self.rho

    def add_density_and_velocity(self, x, y, density, vx, vy):
        self.rho[y, x] += density
        self.u[0, y, x] += vx
        self.u[1, y, x] += vy

    def step(self):
        self.collision()
        self.streaming()
        self.macroscopic()

def initialize_pygame(screen_size):
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('LBM Fluid Simulation')
    return screen

def handle_events(fluid_sim, screen_size, cell_size):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            mouse_x, mouse_y = event.pos
            grid_x, grid_y = mouse_x // cell_size, mouse_y // cell_size
            if 0 <= grid_x < fluid_sim.width and 0 <= grid_y < fluid_sim.height:
                fluid_sim.add_density_and_velocity(grid_x, grid_y, density=1, vx=0.1, vy=0.1)
    return False

def draw_simulation(screen, fluid_sim, screen_size, cell_size):
    screen.fill((0, 0, 0))
    density_scaled = np.clip(fluid_sim.rho * 255, 0, 255).astype(np.uint8)
    surface = pygame.surfarray.make_surface(np.transpose(density_scaled))
    surface = pygame.transform.scale(surface, screen_size)
    screen.blit(surface, (0, 0))
    pygame.display.flip()

def main():
    screen_size = (800, 600)
    cell_size = 4
    grid_width = screen_size[0] // cell_size
    grid_height = screen_size[1] // cell_size
    tau = 0.6 

    fluid_sim = LBMFluidSimulation(grid_width, grid_height, tau)

    screen = initialize_pygame(screen_size)
    clock = pygame.time.Clock()
    done = False

    while not done:
        done = handle_events(fluid_sim, screen_size, cell_size)
        fluid_sim.step()
        draw_simulation(screen, fluid_sim, screen_size, cell_size)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
