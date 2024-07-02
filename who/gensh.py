#!/usr/bin/env python3
# encoding: utf-8

import pygame
import sys
import random
from PIL import Image, ImageSequence

# 初始化 Pygame
pygame.init()

# 设置窗口尺寸
screen_width, screen_height = 400, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('抽卡程序')

class GachaProgram:
    def __init__(self):
        self.gif_frames = self.load_gif('choose_5.gif')
        self.num_frames = len(self.gif_frames)
        self.frame_index = 0
        self.clock = pygame.time.Clock()
        self.showing_gif = False
        self.show_gif_start_time = 0
        self.show_result_time = 2000  # 抽卡结果显示时间，单位毫秒
        self.result_images = ['card_1.jpg', 'card_2.jpg', 'card_3.jpg']  # 抽卡结果图片列表
        self.result_image = None
        self.background = pygame.image.load('back.jpg')  # 主界面背景图片
        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        
        # 字体设置
        self.font_name = "SimHei"  # 字体名称
        self.font_size = 36  # 字体大小
        self.font_color = (255, 0, 255)  # 字体颜色
        self.font = pygame.font.SysFont(self.font_name, self.font_size)  # 字体对象
        self.shadow_color = (0, 0, 0)  # 阴影颜色
        self.shadow_offset = 2  # 阴影偏移

    def load_gif(self, filename):
        # 使用 Pillow (PIL) 加载 GIF 并拆分成帧
        gif = Image.open(filename)
        frames = []
        for frame in ImageSequence.Iterator(gif):
            frames.append(frame.convert('RGB'))  # 转换成 RGB 格式
        return frames

    def start_gacha(self):
        self.showing_gif = True
        self.show_gif_start_time = pygame.time.get_ticks()
        self.frame_index = 0  # 重置 GIF 帧索引

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.showing_gif:
                    if self.result_image is None:
                        self.start_gacha()
                    else:
                        self.result_image = None  # 回到主界面

        # 渲染主界面背景
        if not self.showing_gif and self.result_image is None:
            screen.blit(self.background, (0, 0))
            self.render_text_with_background('Start', screen_width // 2, screen_height // 2)

        # 渲染和显示 GIF 图片
        if self.showing_gif:
            current_frame = self.gif_frames[self.frame_index]
            frame_surface = pygame.image.fromstring(current_frame.tobytes(), current_frame.size, 'RGB')
            frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))  # 调整大小以适应窗口
            screen.blit(frame_surface, (0, 0))

            # 更新帧索引
            self.frame_index = (self.frame_index + 1) % self.num_frames

            # 控制显示时间为指定时间后显示抽卡结果
            if pygame.time.get_ticks() - self.show_gif_start_time > self.show_result_time:
                self.showing_gif = False
                self.show_gacha_result()

        # 显示抽卡结果
        if self.result_image is not None:
            screen.blit(self.result_image, (0, 0))

        pygame.display.flip()
        self.clock.tick(10)  # 控制帧率为 30 FPS

    def render_text_with_background(self, text, x, y):
        text_surface = self.font.render(text, True, self.font_color)
        text_rect = text_surface.get_rect(center=(x, y))
        
        # 绘制阴影效果
        for dx in range(-self.shadow_offset, self.shadow_offset + 1):
            for dy in range(-self.shadow_offset, self.shadow_offset + 1):
                if dx != 0 or dy != 0:
                    shadow_surface = self.font.render(text, True, self.shadow_color)
                    shadow_rect = shadow_surface.get_rect(center=(x + dx, y + dy))
                    screen.blit(shadow_surface, shadow_rect)
        
        # 绘制文本背景
        bg_rect = text_rect.inflate(10, 10)  # 增加背景的大小
        pygame.draw.rect(screen, (255, 255,255), bg_rect)  # 背景颜色为黑色
        screen.blit(text_surface, text_rect)

    def show_gacha_result(self):
        # 随机选择一张抽卡结果图片
        chosen_image = random.choice(self.result_images)
        self.result_image = pygame.image.load(chosen_image)
        self.result_image = pygame.transform.scale(self.result_image, (screen_width, screen_height))

def main():
    gacha_program = GachaProgram()

    running = True
    while running:
        gacha_program.update()

if __name__ == '__main__':
    main()
