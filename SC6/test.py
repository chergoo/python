#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import filedialog
import base64
import os

# 创建文件选择窗口
root = tk.Tk()
root.withdraw()  # 隐藏主窗口
file_path = filedialog.askopenfilename(title="选择图片")
name = os.path.basename(file_path)

if file_path:
   
    # 读取图片并转换为 Base64 编码
    with open(file_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    # 将 Base64 编码写入文本文件
    with open(f'{name}_base64.txt', 'w') as file:
        file.write(encoded_string)
    # 输出 Base64 数据（可省略）
    print(encoded_string)
    
else:
    print("未选择文件")



