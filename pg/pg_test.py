#!/usr/bin/env python3
# encoding: utf-8

import pygame
import sys
import random
# 初始化 Pygame
pygame.init()

# 设置屏幕大小
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('move')

# 加载图片
image = pygame.image.load('kafuka.jpg')
rect = image.get_rect()

# 设置初始速度
speed = [1, 1]

# 初始背景颜色
background_color = (0, 0, 0)

# 随机生成颜色的函数
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # 移动图片
    rect = rect.move(speed)
    
    # 碰到边缘时改变方向
    if rect.left < 0 or rect.right > screen.get_width():
        speed[0] = -speed[0]
        background_color = random_color()
    if rect.top < 0 or rect.bottom > screen.get_height():
        speed[1] = -speed[1]
        background_color = random_color()
    
    # 绘制
    screen.fill(background_color)
    screen.blit(image, rect)
    pygame.display.flip()

    # 控制帧率
    pygame.time.Clock().tick(60)
