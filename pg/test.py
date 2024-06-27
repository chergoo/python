#!/usr/bin/env python3
# encoding: utf-8

import pygame
import sys
from PIL import Image

# 初始化 Pygame
pygame.init()

# 设置屏幕大小
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('缩放动图移动')

# 加载 GIF 动图并分解为帧，并进行缩放
gif = Image.open('choose_5.gif')
frames = []
scale_factor = 0.5  # 缩放比例
try:
    while True:
        frame = gif.copy()
        frame = frame.resize((int(frame.width * scale_factor), int(frame.height * scale_factor)), Image.Resampling.LANCZOS)
        frames.append(pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode))
        gif.seek(len(frames))  # 跳转到下一帧
except EOFError:
    pass

# 获取图片的初始位置
frame_rect = frames[0].get_rect()
frame_rect.topleft = (100, 100)  # 可以设置为你想要的初始位置

# 设置初始速度
speed = [2, 2]
frame_index = 0

# 初始背景颜色
background_color = (0, 0, 0)

# 随机生成颜色的函数
def random_color():
    import random
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # 移动图片
    frame_rect = frame_rect.move(speed)
    
    # 碰到边缘时改变方向并改变背景颜色
    if frame_rect.left < 0 or frame_rect.right > screen.get_width():
        speed[0] = -speed[0]
        background_color = random_color()
    if frame_rect.top < 0 or frame_rect.bottom > screen.get_height():
        speed[1] = -speed[1]
        background_color = random_color()
    
    # 绘制
    screen.fill(background_color)
    screen.blit(frames[frame_index], frame_rect)
    pygame.display.flip()
    
    # 控制帧率和帧动画
    frame_index = (frame_index + 1) % len(frames)
    pygame.time.Clock().tick(10)  # 控制 GIF 帧率
    
    # 控制移动帧率
    pygame.time.delay(20)

