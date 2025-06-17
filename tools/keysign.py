import keyboard
import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard as pynput_keyboard

class KeyPressApp:
    def __init__(self, root):
        self.root = root
        self.root.title("按键/鼠标点击显示器")
        self.root.geometry("240x100+100+100") # 调整窗口高度，更紧凑
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        # 设置透明背景（仅Windows支持）
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.configure(bg="white")

        self.pressed_keys = set()
        self.pressed_mouse_buttons = set()
        # self.last_displayed_text = "无" # 不再需要，删除

        # --- 布局容器 ---
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 文本显示区域 (左侧) - 只显示当前操作
        self.text_frame = tk.Frame(self.main_frame, bg="white")
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 5))

        # 鼠标图示区域 (右侧)
        self.mouse_canvas = tk.Canvas(self.main_frame, width=80, height=120, bg="white", highlightthickness=0) # 调整高度
        self.mouse_canvas.pack(side=tk.RIGHT, padx=10)

        # --- 鼠标图示绘制 ---
        # 绘制背景灰色全圆作为鼠标主体
        self.mouse_canvas.create_oval(15, 20, 65, 70, fill="#E0E0E0", outline="#A0A0A0") # 调整Y坐标
        # 绘制左半圆和右半圆
        self.left_half_circle_id = self.mouse_canvas.create_arc(15, 20, 65, 70, # 调整Y坐标
                                                                 start=90, extent=180,
                                                                 fill="#CCCCCC", outline="#A0A0A0", style=tk.PIESLICE)
        self.right_half_circle_id = self.mouse_canvas.create_arc(15, 20, 65, 70, # 调整Y坐标
                                                                  start=270, extent=180,
                                                                  fill="#CCCCCC", outline="#A0A0A0", style=tk.PIESLICE)

        # --- 文本显示标签 ---
        self.current_label = ttk.Label(
            self.text_frame,
            text=" ",
            font=("Comic Sans MS", 28, "bold"), # 字体可以适当调大一些，因为空间更集中了
            foreground="hot pink",
            background="white"
        )
        # 使用 grid 布局，并调整 pady 使其垂直居中                                                      
        self.current_label.grid(row=0, column=0, pady=(0, 0), sticky="nsew") # 移除下边距，增加上边距以居中

        # self.previous_label 不再创建

        # 确保 text_frame 的列和行可以扩展
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1) # 增加行权重，使内容垂直居中

        # --- Context menu setup ---
        self.context_menu = tk.Menu(root, tearoff=0, bg="#E0E0E0", fg="black",
                                     activebackground="#C0C0C0", activeforeground="black")
        self.context_menu.add_command(label="关闭窗口", command=self.on_closing)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="隐藏窗口", command=self.hide_window)
        self.context_menu.add_command(label="显示窗口", command=self.show_window)

        self.root.bind("<Button-3>", self.show_context_menu)
        self.mouse_canvas.bind("<Button-3>", self.show_context_menu)
        self.current_label.bind("<Button-3>", self.show_context_menu)
        # self.previous_label.bind("<Button-3>", self.show_context_menu) # 删除绑定
        # --- Context menu setup end ---

        # --- Window Dragging & Resizing Variables ---
        self._x = 0
        self._y = 0
        self._start_x = 0
        self._start_y = 0
        self._resizing = False
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._initial_width = 0
        self._initial_height = 0
        self.RESIZE_HANDLE_SIZE = 10

        # Bind mouse events for dragging and resizing
        self.root.bind("<Button-1>", self.on_mouse_button_down_window)
        self.root.bind("<B1-Motion>", self.on_mouse_drag_window)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_button_up_window)
        self.root.bind("<Motion>", self.on_mouse_motion_window)

        # --- Set up pynput listeners ---
        self.keyboard_listener_global = keyboard.hook(self.on_keyboard_event_global)

        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click_pynput
        )
        self.mouse_listener.start()

        self.keyboard_listener_pynput = pynput_keyboard.Listener(
            on_press=self.on_key_press_pynput,
            on_release=self.on_key_release_pynput
        )
        self.keyboard_listener_pynput.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- Mouse Event Handlers for Window Dragging and Resizing ---
    def on_mouse_button_down_window(self, event):
        self._x = self.root.winfo_x()
        self._y = self.root.winfo_y()
        self._start_x = event.x_root
        self._start_y = event.y_root

        self._initial_width = self.root.winfo_width()
        self._initial_height = self.root.winfo_height()

        if (self._initial_width - event.x <= self.RESIZE_HANDLE_SIZE and
            self._initial_height - event.y <= self.RESIZE_HANDLE_SIZE):
            self._resizing = True
            self._resize_start_x = event.x_root
            self._resize_start_y = event.y_root
        else:
            self._resizing = False

    def on_mouse_drag_window(self, event):
        if self._resizing:
            new_width = self._initial_width + (event.x_root - self._resize_start_x)
            new_height = self._initial_height + (event.y_root - self._resize_start_y)

            min_width = 250 # 调整最小宽度
            min_height = 80 # 调整最小高度

            if new_width < min_width: new_width = min_width
            if new_height < min_height: new_height = min_height

            self.root.geometry(f"{int(new_width)}x{int(new_height)}+{self._x}+{self._y}")
        else:
            delta_x = event.x_root - self._start_x
            delta_y = event.y_root - self._start_y
            self.root.geometry(f"+{self._x + delta_x}+{self._y + delta_y}")

    def on_mouse_button_up_window(self, event):
        self._resizing = False
        self.root.config(cursor="")

    def on_mouse_motion_window(self, event):
        if not self._resizing and not event.state & 0x100:
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()

            if (current_width - event.x <= self.RESIZE_HANDLE_SIZE and
                current_height - event.y <= self.RESIZE_HANDLE_SIZE):
                self.root.config(cursor="sizing_se")
            else:
                self.root.config(cursor="arrow")
    # --- End of Window Event Handlers ---

    # --- pynput Listener Callbacks ---
    def on_key_press_pynput(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).replace('Key.', '')

        if key_name and key_name not in self.pressed_keys:
            # self.last_displayed_text = self.get_current_display_text_for_previous() # 不再需要
            self.pressed_keys.add(key_name)
            self.update_display()
            # self.update_previous_label_if_all_released() # 不再需要

    def on_key_release_pynput(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).replace('Key.', '')

        if key_name in self.pressed_keys:
            self.pressed_keys.remove(key_name)
            self.update_display()
            # self.update_previous_label_if_all_released() # 不再需要


    def on_mouse_click_pynput(self, x, y, button, pressed):
        button_name = str(button).replace('Button.', '')

        active_color = "#16B2DA" # 绿色
        inactive_color = "#CCCCCC" # 初始灰色

        if button_name == 'left':
            color = active_color if pressed else inactive_color
            self.mouse_canvas.itemconfig(self.left_half_circle_id, fill=color, outline="#00AA00" if pressed else "#A0A0A0")
        elif button_name == 'right':
            color = active_color if pressed else inactive_color
            self.mouse_canvas.itemconfig(self.right_half_circle_id, fill=color, outline="#00AA00" if pressed else "#A0A0A0")

        if pressed: # Mouse button down
            if button_name not in self.pressed_mouse_buttons:
                # self.last_displayed_text = self.get_current_display_text_for_previous() # 不再需要
                self.pressed_mouse_buttons.add(button_name)
                self.update_display()
        else: # Mouse button up
            if button_name in self.pressed_mouse_buttons:
                self.pressed_mouse_buttons.remove(button_name)
            self.update_display()
            # self.update_previous_label_if_all_released() # 不再需要

    # --- 辅助方法删除 ---
    # def update_previous_label_if_all_released(self): # 不再需要，删除
    # def get_current_display_text_for_previous(self): # 不再需要，删除

    # --- End of pynput Listener Callbacks ---

    def on_keyboard_event_global(self, event):
        if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
            self.on_closing()

    def get_current_display_text(self):
        # 文本显示只包含键盘按键
        all_pressed_keys = sorted(list(self.pressed_keys))
        if all_pressed_keys:
            return " + ".join(all_pressed_keys)
        return " "


    def update_display(self):
        display_text = self.get_current_display_text()
        self.current_label.config(text=display_text)


    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)

    def on_closing(self):
        if self.mouse_listener and self.mouse_listener.running:
            self.mouse_listener.stop()
        if self.keyboard_listener_pynput and self.keyboard_listener_pynput.running:
            self.keyboard_listener_pynput.stop()
        if self.keyboard_listener_global:
            keyboard.unhook(self.keyboard_listener_global)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyPressApp(root)
    root.mainloop()