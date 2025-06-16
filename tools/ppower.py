#!/usr/bin/env python3
# encoding: utf-8
# powerpoint计时器
# 监控PPT放映状态，若检测到放映则弹出计时窗口
import time
import tkinter as tk
import threading
import pygetwindow as gw

def is_ppt_fullscreen():
    for win in gw.getAllWindows():
        if win.visible and win.width >= 1000 and win.height >= 700:
            if win.title.lower().endswith('.pptx') or 'powerpoint' in win.title.lower():
                return True
    return False

def start_timer_window():
    start_time = time.time()

    def update():
        elapsed = int(time.time() - start_time)
        label.config(text=f"放映计时\n{elapsed} 秒")
        if is_ppt_fullscreen():
            root.after(1000, update)
        else:
            root.destroy()

    root = tk.Tk()
    root.overrideredirect(True)  # 去除边框和控制栏
    root.attributes('-topmost', True)  # 始终置顶
    root.configure(bg='black')  # 背景色
    root.geometry("150x80+100+100")  # 位置与大小

    label = tk.Label(root, text="放映计时\n0 秒", font=("微软雅黑", 14), fg='white', bg='black')
    label.pack(expand=True)

    update()
    root.mainloop()

def monitor_ppt():
    print("正在监控 PPT 是否放映...")
    while True:
        if is_ppt_fullscreen():
            print("检测到 PPT 放映，弹出计时窗口")
            threading.Thread(target=start_timer_window).start()
            while is_ppt_fullscreen():
                time.sleep(1)
        time.sleep(2)

if __name__ == '__main__':
    monitor_ppt()
