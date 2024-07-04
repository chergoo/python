import tkinter as tk
import threading
import time

def check_clipboard():
    global last_clipboard_content
    current_clipboard_content = root.clipboard_get()
    print(current_clipboard_content)
    if current_clipboard_content != last_clipboard_content:
        last_clipboard_content = current_clipboard_content
        formatted_text = f'"{current_clipboard_content.strip()}",'
        write_to_file(formatted_text)
    root.after(1000, check_clipboard)  # 每秒检查一次剪贴板内容

def write_to_file(text):
    with open('selected_text.txt', 'a', encoding='utf-8') as file:
        file.write(text + '\n')

# 创建主窗口
root = tk.Tk()
root.title("Clipboard Watcher")

# 开始监视剪贴板内容
last_clipboard_content = root.clipboard_get()
check_clipboard()

# 运行主循环
root.mainloop()
