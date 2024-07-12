#!/usr/bin/env python3
# encoding: utf-8

import pygame
import sys
import win32gui
import win32con
import win32api
from PIL import Image
import datetime

# 宠物状态类
class PetState:
    NORMAL = 'normal'
    HUNGRY = 'hungry'
    HAPPY = 'happy'

# 启动状态类
class StartState:
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    EVENING = 'evening'

# 初始化Pygame
pygame.init()

# 获取屏幕尺寸
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h

# 加载GIF动画的帧
def load_gif_frames(filename):
    frames = []
    image = Image.open(filename)
    for frame in range(image.n_frames):
        image.seek(frame)
        new_frame = image.convert("RGBA")
        frames.append(pygame.image.frombuffer(new_frame.tobytes(), new_frame.size, "RGBA"))
    return frames

# 加载宠物图像帧
pet_images = {
    PetState.NORMAL: load_gif_frames('pet_normal.gif'),
    PetState.HUNGRY: load_gif_frames('pet_hungry.gif'),
    PetState.HAPPY: load_gif_frames('pet_happy.gif'),
}

# 根据时间选择启动动画
def get_start_animation():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return load_gif_frames('morning.gif')
    elif 12 <= current_hour < 18:
        return load_gif_frames('afternoon.gif')
    else:
        return load_gif_frames('evening.gif')

start_frames = get_start_animation()
start_frame_count = len(start_frames)
start_current_frame = 0
start_frame_duration = 100  # 每帧持续时间，单位为毫秒
last_start_frame_change_time = pygame.time.get_ticks()

# 设置窗口标题和初始大小
window_size = (screen_width, screen_height)
pygame.display.set_caption('Desktop Pet')

# 创建 Pygame 窗口
screen = pygame.display.set_mode(window_size, pygame.NOFRAME)

# 将窗口设置为透明
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

# 设置窗口透明度和颜色（这里设置透明颜色为黑色）
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# 宠物初始位置（右下角）
pet_rect = start_frames[0].get_rect()
pet_rect.x = screen_width - pet_rect.width
pet_rect.y = screen_height - pet_rect.height

# 记录上次状态切换时间和帧切换时间
last_state_change_time = pygame.time.get_ticks()
last_frame_change_time = pygame.time.get_ticks()

# 记录鼠标拖动状态
dragging = False
mouse_offset_x = 0
mouse_offset_y = 0

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pet_rect.collidepoint(event.pos):
                dragging = True
                mouse_x, mouse_y = event.pos
                mouse_offset_x = pet_rect.x - mouse_x
                mouse_offset_y = pet_rect.y - mouse_y
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if pet_rect.collidepoint(event.pos):
                if dragging or pygame.mouse.get_pressed()[0]:
                    dragging = True
                    mouse_x, mouse_y = event.pos
                    pet_rect.x = mouse_x + mouse_offset_x
                    pet_rect.y = mouse_y + mouse_offset_y

    # 检查是否到了切换启动帧的时间
    current_time = pygame.time.get_ticks()
    if current_time - last_start_frame_change_time >= start_frame_duration:
        start_current_frame = (start_current_frame + 1) % start_frame_count
        pet_image = start_frames[start_current_frame]
        last_start_frame_change_time = current_time

    # 绘制宠物
    screen.fill((0, 0, 0, 0))  # 清屏为透明
    screen.blit(pet_image, pet_rect)  # 绘制宠物图像

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    pygame.time.Clock().tick(30)  # 设置帧率为30帧每秒
