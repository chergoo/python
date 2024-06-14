#!/usr/bin/env python3
# encoding: utf-8


import requests

def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
        return weather
    else:
        return None


import tkinter as tk
import requests

# 获取天气数据的函数
def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
        return weather
    else:
        return None

# 显示天气信息的函数
def show_weather():
    api_key = "your API KEY"  # 替换为你的API密钥
    # city = "Shanghai"  # 替换为你的城市
    cities = ["Shanghai", "Yichang", "Shenzhen"]  # 需要查询天气的城市列表
    weather_infos = []
    for city in cities:
        weather = get_weather(api_key, city)
        if weather:
            weather_info = f"{weather['city']}\nTemperature: {weather['temperature']}°C\nDescription: {weather['description']}\n"
            weather_infos.append(weather_info)
        else:
            weather_infos.append(f"Failed to get weather data for {city}\n")
    
    # 合并所有城市的天气信息
    combined_weather_info = "\n".join(weather_infos)
    
    # 创建窗口
    root = tk.Tk()
    root.title("Today's Weather")
    
    # 创建标签
    label = tk.Label(root, text=combined_weather_info, font=("Helvetica", 16), padx=20, pady=20)
    label.pack()
    
    # 关闭窗口按钮
    button = tk.Button(root, text="Close", command=root.destroy, padx=20, pady=10)
    button.pack()

    # 运行主循环
    root.mainloop()

# 运行显示天气的函数
if __name__ == "__main__":
    show_weather()

# 设置开机启动
# Windows
# 将脚本保存为 weather.py。
# 创建一个批处理文件（例如 start_weather.bat）
# @echo off
# python path\to\weather.py   替换为自己py文件的地址
# 将批处理文件放到启动文件夹中：C:\Users\{Your_Username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
