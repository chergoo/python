#!/usr/bin/env python3
#encoding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 设置画布
fig, ax = plt.subplots()
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_aspect('equal')
ax.axis('off')

# 初始化粒子数据
num_particles = 1000  # 粒子数量
particles, = plt.plot([], [], 'o', color='pink', markersize=1)

# 初始化粒子的位置 (地面随机分布)
x = np.random.uniform(-20, 20, num_particles)
y = np.random.uniform(-20, -18, num_particles)

# 心形目标位置 (基于经典心形参数方程)
t = np.linspace(0, 2 * np.pi, num_particles)
target_x = 16 * np.sin(t) ** 3  # 目标心形 X 坐标
target_y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)  # 目标心形 Y 坐标

# 计算移动步长
step_x = (target_x - x) / 100  # 将每次移动分为 100 帧
step_y = (target_y - y) / 100

# 更新函数
def update(frame):
    global x, y
    if frame < 100:  # 粒子逐步靠近心形
        x += step_x
        y += step_y
    particles.set_data(x, y)
    return particles,

# 动画
ani = FuncAnimation(fig, update, frames=150, interval=50, blit=True)
plt.show()
