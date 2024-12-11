import pygame
import numpy as np

def plot_2d_vorticity(vorticity, cylinder, screen, screen_width, screen_height):
    min_vorticity = np.min(vorticity)
    max_vorticity = np.max(vorticity)
    
    def normalize(vorticity_value):
        return (vorticity_value - min_vorticity) / (max_vorticity - min_vorticity)

    for j in range(vorticity.shape[0]):
        for i in range(vorticity.shape[1]):
            if not cylinder[j, i]:
                norm_value = normalize(vorticity[j, i])
                red = int(norm_value * 255)
                blue = int((1 - norm_value) * 255)
                color = (red, 0, blue)
                pygame.draw.rect(screen, color, (i * 4, j * 4, 4, 4))
def main():
    pygame.init()
    Nx, Ny = 200, 100
    screen_width, screen_height = Nx * 4, Ny * 4 
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("2D Boltzmann Simulation")
    clock = pygame.time.Clock()

    rho0 = 100
    tau = 0.6
    Nt = 4000
    NL = 9
    idxs = np.arange(NL)
    cxs = np.array([0, 0, 1, 1, 1, 0, -1, -1, -1])
    cys = np.array([0, 1, 1, 0, -1, -1, -1, 0, 1])
    weights = np.array([4 / 9, 1 / 9, 1 / 36, 1 / 9, 1 / 36, 1 / 9, 1 / 36, 1 / 9, 1 / 36])

    F = np.ones((Ny, Nx, NL))
    np.random.seed(42)
    F += 0.01 * np.random.randn(Ny, Nx, NL)
    X, Y = np.meshgrid(range(Nx), range(Ny))
    F[:, :, 3] += 2 * (1 + 0.2 * np.cos(2 * np.pi * X / Nx * 4))
    rho = np.sum(F, 2)
    for i in idxs:
        F[:, :, i] *= rho0 / rho

    cylinder = (X - Nx / 4) ** 2 + (Y - Ny / 2) ** 2 < (Ny / 4) ** 2

    running = True
    for it in range(Nt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        for i, cx, cy in zip(idxs, cxs, cys):
            F[:, :, i] = np.roll(F[:, :, i], cx, axis=1)
            F[:, :, i] = np.roll(F[:, :, i], cy, axis=0)

        bndryF = F[cylinder, :]
        bndryF = bndryF[:, [0, 5, 6, 7, 8, 1, 2, 3, 4]]

        rho = np.sum(F, 2)
        ux = np.sum(F * cxs, 2) / rho
        uy = np.sum(F * cys, 2) / rho

        Feq = np.zeros(F.shape)
        for i, cx, cy, w in zip(idxs, cxs, cys, weights):
            Feq[:, :, i] = rho * w * (
                1 + 3 * (cx * ux + cy * uy)
                + 9 * (cx * ux + cy * uy) ** 2 / 2
                - 3 * (ux ** 2 + uy ** 2) / 2
            )
        F += -(1.0 / tau) * (F - Feq)
        F[cylinder, :] = bndryF

        ux[cylinder] = 0
        uy[cylinder] = 0
        vorticity = (np.roll(ux, -1, axis=0) - np.roll(ux, 1, axis=0)) - \
                    (np.roll(uy, -1, axis=1) - np.roll(uy, 1, axis=1))

        screen.fill((0, 0, 0))
        plot_2d_vorticity(vorticity, cylinder, screen, screen_width, screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
