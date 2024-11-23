import pygame
import math

# 초기 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FABRIK Inverse Kinematics with Collision Avoidance")
clock = pygame.time.Clock()

# 관절 초기화 (4개)
joints = [(200, 300), (300, 300), (400, 300), (500, 300),(600, 300),(700, 300),(800, 300)]  # 초기 관절 위치
bone_lengths = [100, 100, 100,100,100,100]  # 각 뼈 길이 (3개의 뼈)

target = (600, 400)  # 목표 위치


def distance(p1, p2):
    """두 점 사이의 거리 계산"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def line_distance(p1, p2, p3, p4):
    """두 선분 사이의 최소 거리 계산"""
    # 벡터를 이용한 거리 계산
    def point_to_line_distance(pt, line_start, line_end):
        px, py = pt
        x1, y1 = line_start
        x2, y2 = line_end
        numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        return numerator / denominator if denominator != 0 else 0

    d1 = point_to_line_distance(p1, p3, p4)
    d2 = point_to_line_distance(p2, p3, p4)
    return min(d1, d2)


def fabrik(joints, target, bone_lengths):
    """FABRIK 알고리즘"""
    # Forward 단계
    joints[-1] = target  # 마지막 관절을 목표 위치로 설정
    for i in range(len(joints) - 2, -1, -1):
        dir_x = joints[i][0] - joints[i + 1][0]
        dir_y = joints[i][1] - joints[i + 1][1]
        length = distance(joints[i], joints[i + 1])
        scale = bone_lengths[i] / length
        joints[i] = (
            joints[i + 1][0] + dir_x * scale,
            joints[i + 1][1] + dir_y * scale,
        )

    # Backward 단계
    joints[0] = (200, 300)  # 루트 관절 고정
    for i in range(1, len(joints)):
        dir_x = joints[i][0] - joints[i - 1][0]
        dir_y = joints[i][1] - joints[i - 1][1]
        length = distance(joints[i], joints[i - 1])
        scale = bone_lengths[i - 1] / length
        joints[i] = (
            joints[i - 1][0] + dir_x * scale,
            joints[i - 1][1] + dir_y * scale,
        )

    return joints


def avoid_collision(joints):
    """충돌 방지"""
    for i in range(len(joints) - 2):
        for j in range(i + 2, len(joints) - 1):  # 인접하지 않은 뼈만 비교
            dist = line_distance(joints[i], joints[i + 1], joints[j], joints[j + 1])
            if dist < 10:  # 임계값(충돌 최소 거리)
                # 충돌 감지 시 약간 회피
                joints[j] = (joints[j][0] + 5, joints[j][1] + 5)
    return joints


# 메인 루프
running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            target = event.pos  # 마우스 위치를 목표로 설정

    # FABRIK 실행
    joints = fabrik(joints, target, bone_lengths)

    # 충돌 회피
    joints = avoid_collision(joints)

    # 시각화
    for i in range(len(joints) - 1):
        pygame.draw.line(screen, (255, 255, 255), joints[i], joints[i + 1], 2)  # 뼈 그리기
    for joint in joints:
        pygame.draw.circle(screen, (0, 255, 0), (int(joint[0]), int(joint[1])), 5)  # 관절 그리기

    pygame.draw.circle(screen, (255, 0, 0), target, 7)  # 목표 표시
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
