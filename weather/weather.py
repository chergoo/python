#!/usr/bin/env python3
# encoding: utf-8


import requests
from dotenv import load_dotenv

def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity":data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }
        return weather
    else:
        return None


import tkinter as tk
import requests
import  os
from termcolor import colored

load_dotenv()
        
YOUR_API_KEY = os.getenv('API_KEY')

# 获取天气数据的函数
def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
   
    data = response.json()
    print(data)
    
    if response.status_code == 200:
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity":data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }
        return weather
    else:
        return None

# 显示天气信息的函数
def show_weather():
    api_key = YOUR_API_KEY  # 替换为你的API密钥
    # city = "Shanghai"  # 替换为你的城市
    cities = ["Shanghai", "Yichang", "Shenzhen"]  # 需要查询天气的城市列表
    weather_infos = []

    # 创建窗口
    root = tk.Tk()
    root.title("Today's Weather")

    for city in cities:
        weather = get_weather(api_key, city)
        Tem_c = weather['temperature']
        RH = weather['humidity']
        Tem_f = Tem_c *9/5 + 32
        T = Tem_f
        HI_f = -42.379 + 2.04901523*T+10.14333127*RH - 0.22475541*T*RH-6.83783*10**(-3)*T**2 - 5.481717*10**(-2)*RH**2 + 1.22874*10**(-3)*T**2*RH+8.5282*10**(-4)*T*RH**2-1.99*10**(-6)*T**2*RH**2

        HI_c = 5/9 * (HI_f-32)  
        if Tem_c >35:
            color_ = "red"
        elif 30 <= Tem_c <= 35:
            color_ = "orange"
        elif 10 <= Tem_c <= 30:
            color_ = "green"
        else :
            color_ = "blue"

        print(Tem_c,RH)
        if weather:
            weather_info = f"{weather['city']}\n温度: {weather['temperature']}°C\n湿度:{weather['humidity']}%\nDescription: {weather['description']}\n酷热指数:{HI_c:.2f}°C\n"
             # 创建标签
            label = tk.Label(root, text=weather_info, font=("Helvetica", 16), padx=20, pady=20,fg=color_)
            label.pack()
    
            weather_infos.append(weather_info)
        else:
            weather_infos.append(f"Failed to get weather data for {city}\n")
    
    # 合并所有城市的天气信息
    combined_weather_info = "\n".join(weather_infos)
    
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
