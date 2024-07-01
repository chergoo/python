#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import colorchooser,font,messagebox,filedialog
import tkinter.ttk as ttk
from PIL import Image
import os

def choose_color():
    # 弹出颜色选择器
    color_code = colorchooser.askcolor(title="选择颜色")
    if color_code:
        rgb, hex_color = color_code
        # label_rgb.config(text=f"RGB: {rgb}")
        # label_hex.config(text=f"16进制: {hex_color}")

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

def gif_to_jpg_converter():
    # 创建一个Tkinter根窗口并隐藏它
    root = tk.Tk()
    root.withdraw()

    # 弹出文件选择对话框，选择GIF文件
    gif_path = filedialog.askopenfilename(title="选择一个GIF文件", filetypes=[("GIF files", "*.gif")])
    print(gif_path)
    # 如果选择了文件，执行拆解操作
    if gif_path:
        output_folder = os.getcwd()  # 使用当前工作目录
        # 打开GIF图像
        with Image.open(gif_path) as im:
            # 遍历每一帧
            for frame in range(im.n_frames):
                im.seek(frame)
                frame_image = im.convert('RGB')  # 将图像转换为RGB模式
                frame_path = os.path.join(output_folder, f"frame_{frame}.jpg")
                frame_image.save(frame_path, format="JPEG")
                print(f"Saved {frame_path}")
        print(f"所有帧已保存到 {output_folder}")
    else:
        print("未选择任何文件")

def create_gif_from_images():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 弹出文件选择对话框让用户选择图片
    filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    image_files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
    
    if not image_files:
        print("No images selected")
        return
    
    # 打开所有选中的图片
    images = [Image.open(img) for img in image_files]
    
    # 弹出保存对话框让用户选择保存GIF文件的位置和名称
    gif_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
    
    if not gif_path:
        print("Save cancelled")
        return
    
    # 保存为GIF图
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=500,  # 每帧显示时间（毫秒）
        loop=0  # 循环次数，0表示无限循环
    )
    
    print(f"GIF saved at {gif_path}")

# 创建主窗口
root = tk.Tk()
root.title("颜色选择器")

# # 创建按钮框架
# frame = tk.Frame(root)
# frame.pack(padx=10, pady=10)

# 添加按钮用于打开颜色选择器
btn_choose_color = tk.Button(root, text="选择颜色", command=choose_color)
btn_choose_color.pack(side=tk.LEFT,padx=10,pady=20) 

# # 标签用于显示选择的颜色的RGB和16进制格式
# label_rgb = tk.Label(root, text="RGB: ")
# label_rgb.pack(pady=10)

# label_hex = tk.Label(root, text="16进制: ")
# label_hex.pack(pady=10)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="显示字体列表", command=show_font_list)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="GIF拆解", command=gif_to_jpg_converter)
btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="GIF合成", command=create_gif_from_images)
btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

# 运行主循环
root.mainloop()
