import pygame
import numpy as np

def plot_2d_vorticity(vorticity, cylinder, screen, screen_width, screen_height): #유체의 와도를 표현해준다. 와도는 유체가 어떤
    min_vorticity = np.min(vorticity)
    max_vorticity = np.max(vorticity)
    
    def normalize(vorticity_value):
        return (vorticity_value - min_vorticity) / (max_vorticity - min_vorticity)

    for j in range(vorticity.shape[0]):
        for i in range(vorticity.shape[1]):
            if not cylinder[j, i]: #경계조건 활성화, 실린더에게는 유체의 흐름을 주지 않는다
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
    pygame.display.set_caption("LBM_cylinder_Simulation")
    clock = pygame.time.Clock()

    rho0 = 100 #여기서부터는 유체의 표현에 필요한 상수들을 정의함
    tau = 0.6
    Nt = 4000
    NL = 9
    idxs = np.arange(NL)
    cxs = np.array([0, 0, 1, 1, 1, 0, -1, -1, -1]) #x,y의 좌표를 나누어서 표시한다
    cys = np.array([0, 1, 1, 0, -1, -1, -1, 0, 1])
    weights = np.array([4 / 9, 1 / 9, 1 / 36, 1 / 9, 1 / 36, 1 / 9, 1 / 36, 1 / 9, 1 / 36]) #각 유체가 흐를 수 있는 확률을 이렇게 둠

    F = np.ones((Ny, Nx, NL))
    np.random.seed(42)
    F += 0.01 * np.random.randn(Ny, Nx, NL) #볼츠만 방법은 각 유체가 흐를 수 있는 확률에 따라 움직임
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
        bndryF = bndryF[:, [0, 5, 6, 7, 8, 1, 2, 3, 4]] #경계조건의 영역을 활성화

        rho = np.sum(F, 2)
        ux = np.sum(F * cxs, 2) / rho
        uy = np.sum(F * cys, 2) / rho

        Feq = np.zeros(F.shape) #collision 과정 적용
        for i, cx, cy, w in zip(idxs, cxs, cys, weights):
            Feq[:, :, i] = rho * w * (
                1 + 3 * (cx * ux + cy * uy)
                + 9 * (cx * ux + cy * uy) ** 2 / 2
                - 3 * (ux ** 2 + uy ** 2) / 2
            )
        F += -(1.0 / tau) * (F - Feq)
        F[cylinder, :] = bndryF

        ux[cylinder] = 0
        uy[cylinder] = 0 #경계 조건의 속도를 고정, 해당 위치에서는 절대 유체가 흐르지 않도록 만든다
        vorticity = (np.roll(ux, -1, axis=0) - np.roll(ux, 1, axis=0)) - \
                    (np.roll(uy, -1, axis=1) - np.roll(uy, 1, axis=1))

        screen.fill((0, 0, 0))
        plot_2d_vorticity(vorticity, cylinder, screen, screen_width, screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
