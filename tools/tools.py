#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import colorchooser,font,messagebox
import tkinter.ttk as ttk

def choose_color():
    # 弹出颜色选择器
    color_code = colorchooser.askcolor(title="选择颜色")
    if color_code:
        rgb, hex_color = color_code
        label_rgb.config(text=f"RGB: {rgb}")
        label_hex.config(text=f"16进制: {hex_color}")

def get_font_list():
    # 获取系统中可用的字体列表
    system_fonts = font.families()
    return system_fonts

def copy_font_name(event):
    # 复制选中的字体名
    widget = event.widget
    selected_index = widget.curselection()
    if selected_index:
        font_name = widget.get(selected_index[0])
        root.clipboard_clear()
        root.clipboard_append(font_name)
        messagebox.showinfo("复制成功", f"已复制字体名 '{font_name}'")

def show_font_list():
    # 创建一个新的顶级窗口来显示字体列表
    font_list_window = tk.Toplevel(root)
    font_list_window.title("可用字体列表")

    # Frame 用于放置字体列表和滚动条
    frame_font_list = tk.Frame(font_list_window)
    frame_font_list.pack(padx=20, pady=20)

    # 创建滚动条
    scrollbar = tk.Scrollbar(frame_font_list)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 创建 Listbox 用于显示字体列表
    font_listbox = tk.Listbox(frame_font_list, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, width=40, height=10)
    scrollbar.config(command=font_listbox.yview)

    # 获取并显示字体列表
    fonts = get_font_list()
    for font_name in fonts:
        font_listbox.insert(tk.END, font_name)

    font_listbox.pack(side=tk.LEFT)

    # 绑定双击事件，复制选中的字体名
    font_listbox.bind("<Double-Button-1>", copy_font_name)



# 创建主窗口
root = tk.Tk()
root.title("颜色选择器")

# 添加按钮用于打开颜色选择器
btn_choose_color = tk.Button(root, text="选择颜色", command=choose_color)
btn_choose_color.pack(pady=20)

# 标签用于显示选择的颜色的RGB和16进制格式
label_rgb = tk.Label(root, text="RGB: ")
label_rgb.pack(pady=10)

label_hex = tk.Label(root, text="16进制: ")
label_hex.pack(pady=10)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="显示字体列表", command=show_font_list)
btn_show_font_list.pack(pady=20)
# 运行主循环
root.mainloop()
