# import tkinter as tk
# from tkinter import ttk, messagebox
# import serial.tools.list_ports
# import serial
# import threading
# from datetime import datetime
# import time

# # 全局变量
# ser = None
# current_status = None
# log_file = open("log.txt", "a")  # 打开日志文件

# def get_available_ports():
#     """获取可用的COM口"""
#     ports = serial.tools.list_ports.comports()
#     return [port.device for port in ports]

# def refresh_ports():
#     """刷新COM口列表"""
#     ports = get_available_ports()
#     port_combobox['values'] = ports
#     if ports:
#         port_combobox.current(0)  # 默认选择第一个COM口
#     else:
#         port_combobox.set('')  # 清空选择

# def connect_serial():
#     """连接串口"""
#     global ser
#     port = port_combobox.get()
#     if not port:
#         messagebox.showerror("错误", "请选择COM口")
#         return
#     try:
#         ser = serial.Serial(port, baudrate=115200, timeout=1)
#         messagebox.showinfo("成功", f"已连接到 {port}")
#         start_reading_thread()
#     except Exception as e:
#         messagebox.showerror("错误", f"连接失败: {e}")

# def start_reading_thread():
#     """启动串口读取线程"""
#     threading.Thread(target=read_serial, daemon=True).start()

# def read_serial():
#     """读取串口数据"""
#     global current_status
#     while ser and ser.is_open:
#         if ser.in_waiting > 0:
#             data = ser.readline().decode('ascii').strip()
#             if "ON" in data:
#                 update_status("有人")
#             elif "OFF" in data:
#                 update_status("没人")
#         else:
#             time.sleep(0.1)

# def update_status(status):
#     """更新状态并记录日志"""
#     global current_status
#     if status != current_status:  # 状态发生变化
#         current_status = status
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         log_message = f"{timestamp} - Status changed to: {status}\n"
#         status_label.config(text=f"当前状态: {status}")
#         log_text.insert(tk.END, log_message)
#         log_file.write(log_message)
#         log_file.flush()

# def on_closing():
#     """关闭窗口时的操作"""
#     if ser and ser.is_open:
#         ser.close()
#     log_file.close()
#     root.destroy()

# # 创建主窗口
# root = tk.Tk()
# root.title("串口通信程序")

# # 添加COM口选择框
# port_frame = ttk.Frame(root)
# port_frame.pack(pady=10)
# ttk.Label(port_frame, text="选择COM口:").pack(side=tk.LEFT)
# port_combobox = ttk.Combobox(port_frame)
# port_combobox.pack(side=tk.LEFT, padx=10)
# refresh_button = ttk.Button(port_frame, text="刷新", command=refresh_ports)
# refresh_button.pack(side=tk.LEFT, padx=10)
# connect_button = ttk.Button(port_frame, text="连接", command=connect_serial)
# connect_button.pack(side=tk.LEFT)

# # 初始化COM口列表
# refresh_ports()

# # 添加状态显示
# status_label = ttk.Label(root, text="当前状态: 未知", font=("Arial", 16))
# status_label.pack(pady=20)

# # 添加日志显示
# log_text = tk.Text(root, height=10, width=50)
# log_text.pack(pady=10)

# # 设置关闭窗口时的操作
# root.protocol("WM_DELETE_WINDOW", on_closing)

# # 运行主循环
# root.mainloop()

import tkinter as tk
import random
import time

def shake_window(window, intensity=10, duration=0.5):
    """
    使窗口震动
    :param window: 要震动的窗口
    :param intensity: 震动强度（像素）
    :param duration: 震动持续时间（秒）
    """
    start_time = time.time()
    original_x = window.winfo_x()  # 窗口原始X坐标
    original_y = window.winfo_y()  # 窗口原始Y坐标

    while time.time() - start_time < duration:
        # 随机生成偏移量
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        
        # 移动窗口
        window.geometry(f"+{original_x + offset_x}+{original_y + offset_y}")
        window.update()  # 更新窗口
        time.sleep(0.02)  # 控制震动频率

    # 恢复窗口到原始位置
    window.geometry(f"+{original_x}+{original_y}")

# 创建主窗口
root = tk.Tk()
root.title("屏幕震动效果")
root.geometry("300x200")

# 添加按钮，点击后触发震动效果
button = tk.Button(root, text="震动屏幕", command=lambda: shake_window(root))
button.pack(pady=50)

# 运行主循环
root.mainloop()