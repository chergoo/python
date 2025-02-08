#!/usr/bin/env python3
# encoding: utf-8

import pygame
import random
import time

# 初始化Pygame
pygame.init()

# 设置窗口
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("机枪射击模拟")

# 加载资源
background_color = (0, 0, 0)
gunfire_color = (255, 255, 0)
font = pygame.font.Font(None, 36)

# 震动效果
def screen_shake(intensity=5):
    x_offset = random.randint(-intensity, intensity)
    y_offset = random.randint(-intensity, intensity)
    return x_offset, y_offset

# 主循环
running = True
is_firing = False
last_shot_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # 按下空格键射击
                is_firing = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                is_firing = False

    # 绘制背景
    screen.fill(background_color)

    # 模拟射击
    if is_firing:
        current_time = time.time()
        if current_time - last_shot_time > 0.1:  # 控制射速
            pygame.draw.circle(screen, gunfire_color, (400, 300), 10)  # 枪口火焰
            last_shot_time = current_time
        shake = screen_shake(10)
        screen.blit(screen.copy(), shake)

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    pygame.time.delay(30)

pygame.quit()
