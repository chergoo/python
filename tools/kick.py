import threading
import time
import tkinter as tk
from tkinter import messagebox

import pyautogui
from pynput import mouse, keyboard

# 安全设置
pyautogui.FAILSAFE = True
pyautogui.MINIMUM_SLEEP = 0.01


class MouseClickerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("鼠标连点器")
        self.root.geometry("340x220")
        self.root.resizable(False, False)

        # 状态变量
        self.clicking = False
        self.click_thread = None
        self.click_x = None
        self.click_y = None
        self.coord_set = False        # 是否已捕获坐标

        # 监听器
        self.mouse_listener = None
        self.keyboard_listener = None
        self.hotkey = None

        self.create_widgets()
        self.setup_global_hotkey()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # 标题
        tk.Label(self.root, text="鼠标连点器", font=("Arial", 16, "bold")).pack(pady=5)

        # 说明
        info = "操作步骤：\n1. 点击【捕获坐标】按钮\n2. 在屏幕上单击目标位置\n3. 点击【开始】按钮，将以1秒间隔连点\n4. 按 Ctrl+Z 或【停止】可中断"
        tk.Label(self.root, text=info, justify=tk.LEFT, font=("Arial", 9)).pack(pady=5)

        # 坐标显示
        self.coord_label = tk.Label(self.root, text="当前目标: 未设置", fg="blue", font=("Arial", 10))
        self.coord_label.pack(pady=5)

        # 状态显示
        self.status_label = tk.Label(self.root, text="状态: 空闲", fg="gray", font=("Arial", 10))
        self.status_label.pack(pady=5)

        # 按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.capture_btn = tk.Button(btn_frame, text="捕获坐标", command=self.start_capture,
                                     width=12, bg="#2196F3", fg="white")
        self.capture_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(btn_frame, text="开始连点", command=self.start_clicking,
                                   width=12, bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="停止连点", command=self.stop_clicking,
                                  width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 提示
        tk.Label(self.root, text="提示: 将鼠标移到屏幕左上角可紧急停止", font=("Arial", 8), fg="gray").pack(side=tk.BOTTOM, pady=5)

    def setup_global_hotkey(self):
        def on_activate():
            self.root.after(0, self.quit_program)

        self.hotkey = keyboard.HotKey(keyboard.HotKey.parse("<ctrl>+z"), on_activate)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def on_key_press(self, key):
        self.hotkey.press(self.keyboard_listener.canonical(key))

    def on_key_release(self, key):
        self.hotkey.release(self.keyboard_listener.canonical(key))

    def start_capture(self):
        """开始捕获坐标（不自动连点）"""
        if self.clicking:
            self.stop_clicking()

        self.capture_btn.config(state=tk.DISABLED, text="捕获中...")
        self.status_label.config(text="状态: 请单击屏幕选择目标", fg="orange")

        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click_capture)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

    def on_mouse_click_capture(self, x, y, button, pressed):
        if button == mouse.Button.left and pressed:
            self.click_x, self.click_y = x, y
            self.coord_set = True

            # 更新UI
            self.root.after(0, self.update_coord_display)
            self.root.after(0, self.finish_capture)

            # 停止鼠标监听
            if self.mouse_listener and self.mouse_listener.is_alive():
                self.mouse_listener.stop()

    def update_coord_display(self):
        self.coord_label.config(text=f"当前目标: ({self.click_x}, {self.click_y})")

    def finish_capture(self):
        """捕获完成后的UI恢复"""
        self.capture_btn.config(state=tk.NORMAL, text="捕获坐标")
        self.status_label.config(text="状态: 坐标已捕获，可点击【开始】", fg="blue")
        # 启用开始按钮
        self.start_btn.config(state=tk.NORMAL)

    def start_clicking(self):
        """手动开始连点"""
        if not self.coord_set or self.click_x is None:
            messagebox.showwarning("警告", "请先捕获坐标再开始连点")
            return

        if self.clicking:
            return

        self.clicking = True
        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()

        # UI更新
        self.status_label.config(text="状态: 连点中 (间隔1秒)", fg="green")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.capture_btn.config(state=tk.DISABLED)

    def click_loop(self):
        while self.clicking:
            pyautogui.click(self.click_x, self.click_y)
            # 以0.1秒粒度检查停止标志，保证及时响应
            for _ in range(10):
                if not self.clicking:
                    break
                time.sleep(0.1)

    def stop_clicking(self):
        if not self.clicking:
            return
        self.clicking = False
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)

        self.status_label.config(text="状态: 已停止", fg="gray")
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL if self.coord_set else tk.DISABLED)
        self.capture_btn.config(state=tk.NORMAL)

    def quit_program(self):
        self.stop_clicking()
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
        self.root.quit()
        self.root.destroy()

    def on_closing(self):
        self.quit_program()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MouseClickerApp()
    app.run()