import time
import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageDraw  
import pystray  
#一个闹钟小脚本，可以设置闹钟时间和闹钟提示语，到时间后会弹出提示框，提示框会震动一下
def set_alarm():
    # 获取用户输入的时间
    alarm_time = entry.get()
    alarm_sign = entry1.get()
    try:
        # 将输入的时间转换为时间元组
        alarm_hour, alarm_minute = map(int, alarm_time.split(':'))
        while True:
            # 获取当前时间
            current_time = time.localtime()
            current_hour, current_minute = current_time.tm_hour, current_time.tm_min

            # 检查是否到达设定时间
            if (current_hour == alarm_hour) and (current_minute == alarm_minute):
                # 创建弹窗窗口
                alert_window = tk.Toplevel()
                alert_window.title("闹钟提醒")
                # 设置背景颜色
                alert_window.configure(bg="lightblue")  # 使用颜色名称或十六进制值
                alert_window.attributes("-topmost", True)  # 设置为置顶窗口

                # 添加提醒内容
                label = tk.Label(alert_window, text=alarm_sign, font=("Arial", 16))
                label.pack(pady=20, padx=20)

                # 添加关闭按钮
                button = tk.Button(alert_window, text="关闭", command=alert_window.destroy)
                button.pack(pady=10)

                # 让弹窗在屏幕中心显示
                center_window(alert_window)

                intensity = 10
                duration = 0.5

                start_time = time.time()
                # original_x = alert_window.winfo_x()  # 窗口原始X坐标
                # original_y = alert_window.winfo_y()  # 窗口原始Y坐标
                original_x,original_y = center_window(alert_window)
                print("x_","y_",original_x,original_y)

                while time.time() - start_time < duration:
                    # 随机生成偏移量
                    offset_x = random.randint(-intensity, intensity)
                    offset_y = random.randint(-intensity, intensity)
                    
                    # 移动窗口
                    alert_window.geometry(f"+{original_x + offset_x}+{original_y + offset_y}")
                    alert_window.update()  # 更新窗口
                    time.sleep(0.02)  # 控制震动频率

                # 恢复窗口到原始位置
                alert_window.geometry(f"+{original_x}+{original_y}")

                break
            # 每隔一秒检查一次
            time.sleep(1)
    except ValueError:
        messagebox.showerror("错误", "请输入正确的时间格式（HH:MM）")

def center_window(window):
    """
    将窗口居中显示在屏幕上
    """
    window.update_idletasks()  # 更新窗口布局
    width = window.winfo_width()  # 获取窗口宽度
    height = window.winfo_height()  # 获取窗口高度
    screen_width = window.winfo_screenwidth()  # 获取屏幕宽度
    screen_height = window.winfo_screenheight()  # 获取屏幕高度

    # 计算窗口居中时的坐标
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    print("x","y",x,y)

    # 设置窗口位置
    window.geometry(f"+{x}+{y}")
    return x,y

def on_closing():
    # 弹出确认对话框
    if messagebox.askokcancel("退出", "确定要退出吗？"):
        root.destroy()  # 关闭窗口

def create_image():
    # 使用你自己的 .ico 文件
    image = Image.open("cat.ico")
    return image

def quit_app(icon, item):
    icon.stop()
    root.destroy()

def show_window(icon, item):
    icon.stop()
    root.after(0, root.deiconify)

def hide_window():
    root.withdraw()
    # image = create_image()
    # menu = (pystray.MenuItem('显示', show_window), pystray.MenuItem('退出', quit_app))
    # icon = pystray.Icon("test", image, "闹钟程序", menu)
    # icon.run()

def setup_tray_icon():
    image = create_image()
    menu = (pystray.MenuItem('显示', show_window), pystray.MenuItem('退出', quit_app))
    icon = pystray.Icon("test", image, "闹钟程序", menu)
    icon.run()

# 创建主窗口
root = tk.Tk()
root.title("闹钟程序")
root.overrideredirect(True)  # 隐藏标题栏和任务栏图标
# 隐藏任务栏图标（仅限 Windows）
# root.wm_attributes("-toolwindow", True)

# 设置关闭事件的处理函数
root.protocol("WM_DELETE_WINDOW", on_closing)

# 添加标签和输入框
label = tk.Label(root, text="请输入闹钟时间（HH:MM）：")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=10)

entry1 = tk.Entry(root)
entry1.pack(pady=10)

# 添加隐藏窗口按钮
button = tk.Button(root, text="-", command=hide_window)  
button.pack(side=tk.LEFT,padx=10,pady=10)

# 添加设置闹钟按钮
button = tk.Button(root, text="设置闹钟", command=set_alarm)
button.pack(side=tk.LEFT,padx=10,pady=10)

#添加退出
button = tk.Button(root, text="×", command=on_closing)
button.pack(side=tk.RIGHT,padx=10,pady=10)

# 启动托盘图标
import threading
threading.Thread(target=setup_tray_icon, daemon=True).start()

# 运行主循环
root.mainloop()