import time
import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageDraw  
import pystray  
import threading

# 全局闹钟状态
alarm_state = {'set': False, 'time': None, 'sign': None}
tray_icon = None
#一个闹钟小脚本，可以设置闹钟时间和闹钟提示语，到时间后会弹出提示框，提示框会震动一下
def set_alarm():
    # 获取用户输入的时间并启动后台线程来监控
    alarm_time = entry.get()
    alarm_sign = entry1.get()
    try:
        alarm_hour, alarm_minute = map(int, alarm_time.split(':'))

        # 更新全局状态
        alarm_state['set'] = True
        alarm_state['time'] = f"{alarm_hour:02d}:{alarm_minute:02d}"
        alarm_state['sign'] = alarm_sign

        # 启动后台线程监控闹钟
        threading.Thread(target=alarm_worker, args=(alarm_hour, alarm_minute, alarm_sign), daemon=True).start()

        # 隐藏主窗口到托盘
        hide_window()

        # 通知托盘图标（如果可用）
        try:
            if tray_icon:
                tray_icon.notify(f"闹钟已设置：{alarm_state['time']} {alarm_sign}")
        except Exception:
            pass
    except ValueError:
        messagebox.showerror("错误", "请输入正确的时间格式（HH:MM）")


def alarm_worker(alarm_hour, alarm_minute, alarm_sign):
    # 在后台循环检查时间
    while alarm_state.get('set'):
        current_time = time.localtime()
        if (current_time.tm_hour == alarm_hour) and (current_time.tm_min == alarm_minute):
            # 触发闹钟
            alarm_state['set'] = False
            # 在主线程创建弹窗和震动效果
            root.after(0, lambda: show_alert(alarm_sign))
            # 托盘通知
            try:
                if tray_icon:
                    tray_icon.notify(f"闹钟响了：{alarm_state['time']} {alarm_sign}")
            except Exception:
                pass
            break
        time.sleep(1)

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
    # print("x","y",x,y)

    # 设置窗口位置
    window.geometry(f"+{x}+{y}")
    return x,y

def shake(window, original_x, original_y, intensity=10, duration=0.5):
    start = time.time()
    def step():
        elapsed = time.time() - start
        if elapsed < duration:
            offset_x = random.randint(-intensity, intensity)
            offset_y = random.randint(-intensity, intensity)
            window.geometry(f"+{original_x + offset_x}+{original_y + offset_y}")
            window.after(20, step)
        else:
            window.geometry(f"+{original_x}+{original_y}")
    step()

def show_alert(alarm_sign):
    # 在主线程显示弹窗并震动
    alert_window = tk.Toplevel()
    alert_window.title("闹钟提醒")
    alert_window.configure(bg="lightblue")
    alert_window.attributes("-topmost", True)

    label = tk.Label(alert_window, text=alarm_sign, font=("Arial", 16))
    label.pack(pady=20, padx=20)
    button = tk.Button(alert_window, text="关闭", command=alert_window.destroy)
    button.pack(pady=10)

    original_x, original_y = center_window(alert_window)
    shake(alert_window, original_x, original_y, intensity=10, duration=0.5)

def on_closing():
    # 弹出确认对话框
    if messagebox.askokcancel("退出", "确定要退出吗？"):
        root.destroy()  # 关闭窗口

def create_image():
    # 使用你自己的 .ico 文件，如果不存在就动态生成一个简单图标
    try:
        image = Image.open("cat.ico")
        return image
    except Exception:
        # 生成简单图像（64x64）
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((8, 8, 56, 56), fill=(255, 165, 0, 255))
        return img

def quit_app(icon, item):
    icon.stop()
    root.destroy()
def show_window(icon, item):
    # 从托盘显示主窗口
    try:
        icon.visible = False
    except Exception:
        pass
    root.after(0, root.deiconify)

def hide_window():
    root.withdraw()
    # 确保托盘图标可见
    try:
        if tray_icon:
            tray_icon.visible = True
    except Exception:
        pass

def show_status(icon, item):
    # 在主线程显示当前闹钟状态
    def _show():
        if alarm_state.get('set'):
            messagebox.showinfo('闹钟状态', f"正在计时\n时间: {alarm_state['time']}\n内容: {alarm_state['sign']}")
        else:
            messagebox.showinfo('闹钟状态', '当前没有设置闹钟')
    root.after(0, _show)

def setup_tray_icon():
    global tray_icon
    image = create_image()
    menu = (pystray.MenuItem('显示', show_window), pystray.MenuItem('状态', show_status), pystray.MenuItem('退出', quit_app))
    tray_icon = pystray.Icon("clolck", image, "闹钟程序", menu)
    try:
        tray_icon.run()
    except Exception:
        pass

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

# 添加时间输入框，并设置默认提示词
entry = tk.Entry(root)
entry.insert(0, "07:30")  # 设置默认提示词
entry.bind("<FocusIn>", lambda event: entry.delete(0, tk.END) if entry.get() == "07:30" else None)
entry.bind("<FocusOut>", lambda event: entry.insert(0, "07:30") if entry.get() == "" else None)
entry.pack(pady=10)

# 添加内容输入框，并设置默认提示词
entry1 = tk.Entry(root)
entry1.insert(0, "闹钟内容")  # 设置默认提示词
entry1.bind("<FocusIn>", lambda event: entry1.delete(0, tk.END) if entry1.get() == "闹钟内容" else None)
entry1.bind("<FocusOut>", lambda event: entry1.insert(0, "闹钟内容") if entry1.get() == "" else None)
entry1.pack(pady=10)

# 添加隐藏窗口按钮
button = tk.Button(root, text="-", command=hide_window)
button.pack(side=tk.LEFT, padx=10, pady=10)

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