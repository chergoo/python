#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from math import pi
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
# from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os
import requests

# 创建主窗口
root = tk.Tk()
root.title("日出日落时间查询-中国")
root.geometry("600x600")

# 设置中文字体
plt.rcParams['font.family'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 标签和输入框：城市名称、纬度、经度和时间
tk.Label(root, text="城市名称:").grid(row=0, column=0)
city_entry = tk.Entry(root)
city_entry.grid(row=0, column=1)
city_entry.insert(0, "上海")  # 默认值为上海

tk.Label(root, text="纬度:").grid(row=1, column=0)
latitude_entry = tk.Entry(root)
latitude_entry.grid(row=1, column=1)
latitude_entry.insert(0, "31.2304")  # 默认值为上海的纬度

tk.Label(root, text="经度:").grid(row=2, column=0)
longitude_entry = tk.Entry(root)
longitude_entry.grid(row=2, column=1)
longitude_entry.insert(0, "121.4737")  # 默认值为上海的经度

tk.Label(root, text="日期 (YYYY-MM-DD):").grid(row=3, column=0)
date_entry = tk.Entry(root)
date_entry.grid(row=3, column=1)
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

# 创建画布
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=4, column=0, columnspan=3)

# 根据城市名称获取经纬度
def get_coordinates_by_city():
    try:
        city_name = city_entry.get()
 # 高德API Key
        load_dotenv()
        YOUR_AMAP_API_KEY = os.getenv('API_KEY')
        url =f'https://restapi.amap.com/v3/geocode/geo?address={city_name}&key={YOUR_AMAP_API_KEY}'
        
        # 发送请求
        response = requests.get(url)
        # print("高德返回的地址",response.text)
        
        # 解析JSON响应
        data = response.json()
        print("1111111111111",data)
        # 检查状态码，确保请求成功
        if data['status'] == '1' and 'geocodes' in data:
            location = data['geocodes'][0]['location']  # 获取location字段
            longitude, latitude = location.split(',')  # 分割经纬度
            print("经度:", longitude)
            print("纬度:", latitude)
        else:
            print('请求失败，错误码：', data['infocode'])
        
    
        # geolocator = Nominatim(user_agent="my_application",timeout=10)
        # location = geolocator.geocode(city_name)
        # print(location)
        # if location is None:
        #     messagebox.showerror("错误", "无法找到该城市，请输入有效的城市名称！")
        #     return
        # # 清空经纬度输入框
        # latitude_entry.delete(0, tk.END)
        # longitude_entry.delete(0, tk.END)

        # 将获取到的经纬度填充到输入框中
        latitude_entry.delete(0, tk.END)
        longitude_entry.delete(0, tk.END)
        latitude_entry.insert(0, latitude)
        longitude_entry.insert(0, longitude)
    except Exception as e:
        messagebox.showerror("错误", f"查询城市经纬度失败: {e}")

# 根据输入生成图像的函数
def generate_sunrise_sunset_plot():
    try:
        # 获取输入的纬度、经度和日期
        latitude = float(latitude_entry.get())
        longitude = float(longitude_entry.get())
        date_str = date_entry.get()
        date = datetime.strptime(date_str, "%Y-%m-%d")
        
         # 获取时区
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
        tz = pytz.timezone(timezone_str)
        # print(timezone_str,tz)
        # 获取日出日落时间
        location = LocationInfo("", "", tz, latitude, longitude)
        s = sun(location.observer, date=date)
        
        # 将UTC时间转换为当地时间
        # tz = pytz.timezone(location.timezone)
        sunrise_time = s['sunrise'].astimezone(tz).time()
        sunset_time = s['sunset'].astimezone(tz).time()

        # 将时间转换为小时表示的浮点数
        sunrise_hour = sunrise_time.hour + sunrise_time.minute / 60
        sunset_hour = sunset_time.hour + sunset_time.minute / 60

        # 计算日出日落角度
        sunrise_angle = (sunrise_hour / 24) * pi+pi/2
        sunset_angle = (sunset_hour / 24) *  pi-pi/2

        # 创建极坐标图
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        angles = np.linspace(0, pi, 100)  # 只绘制半圆弧
        ax.plot(angles, np.ones_like(angles), color='orange', lw=5)

        # 标记日出时间
        ax.text(sunrise_angle, 1.3, f"日升\n{sunrise_time.strftime('%H:%M')}",
                horizontalalignment='left', verticalalignment='center', color='orange', fontsize=12)
        ax.plot(sunrise_angle, 1, 'o', color='orange', markersize=10)

        # 标记日落时间
        ax.text(sunset_angle, 1.3, f"日落\n{sunset_time.strftime('%H:%M')}",
                horizontalalignment='right', verticalalignment='center', color='orange', fontsize=12)
        ax.plot(sunset_angle, 1, 'o', color='orange', markersize=10)

        # 设置背景颜色
        now = datetime.now(tz).time()
        if sunrise_time < now < sunset_time:
            ax.set_facecolor('#fff5e1')
        else:
            ax.set_facecolor("#e1ebff")

        # 设置极坐标图的角度范围，限制在0到π的范围内以只显示半圆
        ax.set_thetamin(0)
        ax.set_thetamax(180)

        # 隐藏不需要的元素
        ax.grid(False)  # 隐藏网格
        ax.set_xticks([])  # 隐藏角度刻度
        ax.set_yticks([])  # 隐藏半径刻度
        ax.spines['polar'].set_visible(False)  # 隐藏外圈

        # 显示时区信息，放在图的下方
        ax.text(0.5, 1, f"时区: {timezone_str}",
            horizontalalignment='center', verticalalignment='center',
            transform=ax.transAxes, color='black', fontsize=14)

        # 清除之前的画布
        for widget in canvas_frame.winfo_children():
            widget.destroy()

        # 在 Tkinter 窗口中显示图像
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的经纬度和日期格式！")

# 创建“查询经纬度”按钮
city_button = tk.Button(root, text="查询城市经纬度", command=get_coordinates_by_city)
city_button.grid(row=0, column=2)

# 创建查询按钮
query_button = tk.Button(root, text="查询", command=generate_sunrise_sunset_plot)
query_button.grid(row=3, column=2, columnspan=2)

# 窗口关闭事件处理
def on_closing():
    if messagebox.askokcancel("退出", "你确定要退出程序吗？"):
        root.quit()

# 绑定关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# 运行Tkinter主循环
root.mainloop()
