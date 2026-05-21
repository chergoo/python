#!/usr/bin/env python3
# encoding: utf-8
# -*- coding: utf-8 -*-

import sys
import io
import time
import threading
import signal
import os
from datetime import datetime

# 第三方库
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pynput import keyboard, mouse
import pytz

# 解决控制台输出编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --------------------------
# 1. 全局配置
# --------------------------

# 存储所有输入事件的时间戳（Unix秒）
input_events = [] 
running = True
log_file = "input_events.txt"

# 设置绘图风格和字体
try:
    # 尝试使用 seaborn 样式，更美观
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    pass

# 设置中文字体 (根据系统自动回退，防止乱码)
plt.rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示为方块的问题

# --------------------------
# 2. 核心逻辑
# --------------------------

def on_input_event(key_or_button):
    """
    键盘和鼠标事件的回调函数。
    直接记录 Unix 时间戳，保持轻量。
    """
    global input_events
    if running:
        input_events.append(time.time())

def start_listeners():
    """启动监听线程"""
    global running
    print(f"🖥️  工作状态监控已启动...")
    print(f"📝 数据将保存至: {os.path.abspath(log_file)}")
    print(f"❌ 按 Ctrl+C 停止监控并生成报表...")

    # 初始化日志文件（清空）
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("时间\t输入次数\n")
    except Exception as e:
        print(f"⚠️  无法初始化日志文件: {e}")

    # 启动监听器
    # 键盘监听
    keyboard_listener = keyboard.Listener(on_press=on_input_event)
    keyboard_listener.daemon = True
    keyboard_listener.start()
    
    # 鼠标监听 (监听点击)
    # 如果想监听移动，加上 on_move=on_input_event，但数据量会极其巨大，不建议
    mouse_listener = mouse.Listener(on_click=on_input_event)
    mouse_listener.daemon = True
    mouse_listener.start()
    
    # 主线程阻塞，等待中断信号
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass 
    finally:
        if keyboard_listener.is_alive():
            keyboard_listener.stop()
        if mouse_listener.is_alive():
            mouse_listener.stop()
        print("\n🛑 监控结束，正在处理数据...")

def visualize_data():
    """数据处理与可视化"""
    
    if not input_events:
        print("⚠️  未收集到任何输入数据，无法绘图。")
        return

    print(f"📊 共捕获 {len(input_events)} 次输入操作。正在计算...")

    # 1. 数据清洗与时区转换
    try:
        # 创建 DataFrame
        df = pd.DataFrame(input_events, columns=['timestamp'])
        
        # 将 Unix 时间戳转换为 UTC 时间对象
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
        
        # 转换为北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        df['datetime'] = df['datetime'].dt.tz_convert(beijing_tz)
        
        # 设置索引用于重采样
        df.set_index('datetime', inplace=True)
        
        # 2. 重采样 (Resample) - 按1分钟聚合
        # '1T' 代表 1分钟。count() 计算该分钟内的行数
        frequency = df.resample('1T')['timestamp'].count()
        
        # 3. 补全空缺时间段 (可选)
        # 如果需要在没有数据的分钟显示为0，Pandas resample 默认会产生 NaN，count() 会变成 0，这正是我们想要的
        
        # 4. 保存统计数据到文件
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("时间\t输入频率(次/分)\n")
            for time_idx, count in frequency.items():
                # 只记录有数据的时刻，或者记录所有时刻（这里记录所有）
                line = f"{time_idx.strftime('%Y-%m-%d %H:%M:%S')}\t{int(count)}\n"
                f.write(line)
        print(f"✅ 统计数据已保存至 {log_file}")

        # 5. 绘图 (Matplotlib)
        plot_graph(frequency)

    except Exception as e:
        print(f"❌ 数据处理出错: {e}")
        import traceback
        traceback.print_exc()

def plot_graph(series_data):
    """独立的绘图函数"""
    plt.figure(figsize=(14, 7))
    
    # 绘制区域填充图 (Area Chart)，比单纯折线更有“工作量”的感觉
    plt.fill_between(series_data.index, series_data.values, color='#1f77b4', alpha=0.3)
    plt.plot(series_data.index, series_data.values, 
             label='操作频率', 
             color='#1f77b4', 
             linewidth=1.5,
             marker='.',          # 使用小点标记
             markersize=5)

    # 标题与标签
    plt.title(f'工作状态可视化 - 输入频率监控 ({series_data.index[0].strftime("%Y-%m-%d")})', fontsize=16, pad=20)
    plt.xlabel('时间', fontsize=12)
    plt.ylabel('每分钟操作数 (键盘+鼠标)', fontsize=12)
    
    # 设置 Y 轴只显示整数
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    
    # 网格线
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # 自动格式化 X 轴时间
    plt.gcf().autofmt_xdate()
    
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    print("🖼️  图表已生成。")
    plt.show()

def stop_script(sig, frame):
    """信号处理函数"""
    global running
    if running:
        running = False
        # 稍微等待主循环退出
        time.sleep(0.5) 
        visualize_data()
        sys.exit(0)

if __name__ == "__main__":
    # 注册信号
    signal.signal(signal.SIGINT, stop_script)
    
    # 启动
    start_listeners()
    
    # 双重保险，防止意外跳出
    stop_script(None, None)