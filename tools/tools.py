#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import colorchooser,font,messagebox,filedialog,font
import tkinter.ttk as ttk
from PIL import Image
import os
import sys
import datetime

def choose_color():
    # 创建一个新的顶级窗口来显示字体列表
        color_window = tk.Toplevel(root)
        color_window.geometry("300x150+150+250")  # 设置窗口大小为300x200，并将左上角定位在屏幕坐标（150，250）
        color_window.title("颜色参数")

        # 使用Entry组件来代替Label，并设置为只读
        entry_rgb = tk.Entry(color_window, width=20, state='readonly')
        entry_hex = tk.Entry(color_window, width=20, state='readonly')
        entry_rgb.pack(pady=10)
        entry_hex.pack()

        color_code = colorchooser.askcolor(title="选择颜色")
        if color_code:
            rgb, hex_color = color_code
            entry_rgb.config(state='normal')  # 设置为可编辑状态
            entry_rgb.delete(0, tk.END)  # 清空之前的内容
            entry_rgb.insert(0, f"RGB: {rgb}")  # 插入新的内容
            entry_rgb.config(state='readonly')  # 设置为只读状态

            entry_hex.config(state='normal')  # 设置为可编辑状态
            entry_hex.delete(0, tk.END)  # 清空之前的内容
            entry_hex.insert(0, f"Hex: {hex_color}")  # 插入新的内容
            entry_hex.config(state='readonly')  # 设置为只读状态

    # # 标签用于显示选择的颜色的RGB和16进制格式
    #     label_rgb = tk.Label(color_window, text="RGB: ")
    #     label_rgb.pack(pady=10)

    #     label_hex = tk.Label(color_window, text="16进制: ")
    #     label_hex.pack(pady=10)

    # # 弹出颜色选择器
    #     color_code = colorchooser.askcolor(title="选择颜色")
    #     print("yansss",color_code)
    #     if color_code:
    #         rgb, hex_color = color_code
    #         label_rgb.config(text=f"RGB: {rgb}")
    #         label_hex.config(text=f"16进制: {hex_color}")

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
        # messagebox.showinfo("复制成功", f"已复制字体名 '{font_name}'")
        # 创建顶层窗口
        top = tk.Toplevel(root)
        top.title("字体选择与预览")
        top.geometry("300x150")
                
        # 创建 Label 小部件并设置字体
        message = ("复制成功", f"已复制字体名 '{font_name}'")
        msg_label = tk.Label(top, text=message)
        msg_label.pack(pady=10)
        Font_Preview = tk.Label(top, text="字体预览--Font Preview", font=(font_name, 12))
        Font_Preview.pack(pady=10)
    
        # 创建 Button 小部件关闭消息框
        ok_button = tk.Button(top, text="确定", command=top.destroy)
        ok_button.pack(pady=5)

       

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
    # 
    font_listbox.pack(side=tk.LEFT)

    # 定义鼠标移动事件处理函数
    def on_mouse_move(event):
        widget = event.widget
        index = widget.nearest(event.y)
        if index >= 0:
            font_name = widget.get(index)
            preview_label.config(font=(font_name, 16), text=font_name) 

    # 绑定双击事件，复制选中的字体名
    font_listbox.bind("<Double-Button-1>", copy_font_name)
    
    # 绑定鼠标移动事件
    font_listbox.bind("<Motion>", on_mouse_move)

    preview_label = tk.Label(font_list_window, text="Preview Text", font=("Arial", 20))
    preview_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    

    

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
        duration=100,  # 每帧显示时间（毫秒）
        loop=0  # 循环次数，0表示无限循环
    )
    
    print(f"GIF saved at {gif_path}")

def time_change():
    # root = tk.Tk()
    # root.withdraw()  # 隐藏主窗口
    root_ = tk.Toplevel(root)  # 创建新的顶级窗口
    label = tk.Label(root_, text="新窗口")
    label.pack

    # 将时间戳转换为datetime对象
    def change_():
     # 清空 Entry 输入框
     entry__time.delete(0, tk.END)
     timestamp = int(entry_time.get())
     
     dt = datetime.datetime.fromtimestamp(timestamp)
    
    # 格式化datetime对象为字符串
     formatted_time = dt.strftime("%m/%d/%y %H:%M:%S")
     entry__time.insert(0, str(formatted_time))
    
    def change():
        entry_time.delete(0, tk.END)
        timestamp_ = entry__time.get()
        # 定义日期时间字符串的格式
        date_format = "%m/%d/%y %H:%M:%S"
        # 将字符串转换为datetime对象
        dt = datetime.datetime.strptime(timestamp_, date_format)
        # 将datetime对象转换为时间戳
        timestamp = int(dt.timestamp())
        entry_time.insert(0, str(timestamp))

    # 第一行：创建标签和输入框
    top_frame = tk.Frame(root_)
    top_frame.pack(pady=10)

    label_time = tk.Label(top_frame, text="时间_数值 ")
    label_time.pack(side=tk.LEFT,padx=10,pady=20)

    # 创建 Entry 小部件，并设置默认值
    entry_time = tk.Entry(top_frame)
    default_value = "1719822360"
    entry_time.insert(0, default_value)
    entry_time.pack(side=tk.LEFT,padx=10,pady=20)

    btn_time = tk.Button(top_frame, text="时间——数值转换", command=change_)
    btn_time.pack(side=tk.LEFT,padx=10,pady=20) 


    # 第二行：创建结果显示的标签和输入框
    middle_frame = tk.Frame(root_)
    middle_frame.pack(pady=10)

    label__time = tk.Label(middle_frame,text="时间_通用")
    label__time.pack(side=tk.LEFT,padx=10,pady=20)
    # 创建 Entry 小部件，并设置默认
    entry__time = tk.Entry(middle_frame)
    default_value = "07/01/24 16:26:00"
    entry__time.insert(0, default_value)
    entry__time.pack(side=tk.LEFT,padx=10,pady=20)
    
    btn__time = tk.Button(middle_frame, text="时间——通用转换", command=change)
    btn__time.pack(side=tk.LEFT,padx=10,pady=20) 

   
# 创建主窗口
root = tk.Tk()
root.title("颜色选择器")

# 当窗口关闭时，调用关闭函数
def on_closing():
    root.quit()
    root.destroy()
    sys.exit()

# 绑定关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# # 创建按钮框架
# frame = tk.Frame(root)
# frame.pack(padx=10, pady=10)

# 添加按钮用于打开颜色选择器
btn_choose_color = tk.Button(root, text="选择颜色", command=choose_color)
btn_choose_color.pack(side=tk.LEFT,padx=10,pady=20) 


# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="显示字体列表", command=show_font_list)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="GIF拆解", command=gif_to_jpg_converter)
btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(root, text="GIF合成", command=create_gif_from_images)
btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

btn_show_font_list = tk.Button(root, text="时间格式转换", command=time_change)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 

root.quit()

# 运行主循环
root.mainloop()
