#!/usr/bin/env python3
# encoding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为中文宋体

# 读取Excel文件
df = pd.read_excel("log.xlsx")

# 将日期转换为datetime格式
df['时间'] = pd.to_datetime(df['时间'], format='%Y%m%d')

# 提取事件时间和名称
times = df['时间'].tolist()
names = df['项目'].tolist()

# 创建图形和轴
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制时间线
ax.plot(times, [1]*len(times), marker='o', linestyle='-', color='b')

# 为每个事件添加标签
for i, (time, name) in enumerate(zip(times, names)):
    ax.text(time, 1, name, rotation=45, ha='right', va='bottom')
    ax.text(time, 0.99, time.strftime('%Y-%m-%d'), rotation=0, ha='right', va='bottom')

# 隐藏X轴和Y轴
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)

# 隐藏图形边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# 设置日期格式
# ax.xaxis.set_major_locator(mdates.FixedLocator(times))  # 设置X轴主刻度为数据中的日期
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())

# 设置X轴的范围为数据中的最小日期到最大日期
ax.set_xlim(min(times), max(times))

# 设置只显示数据中的日期刻度
ax.set_xticks(times)

# 设置图形的格式和标题
plt.title("Project Timeline")
plt.xlabel("Time")
plt.yticks([])  # 隐藏y轴刻度
plt.grid(True)
plt.tight_layout()

# 显示图形
plt.show()

