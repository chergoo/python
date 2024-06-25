#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
import random
from math import cos, sin, radians
from PIL import Image, ImageTk

class RandomSelectorApp:
    def __init__(self, root, grid_names):
        self.root = root
        self.root.title("随机选择方格")
        self.grid_size = 4
        self.grid_names = grid_names
        self.buttons = []
        self.running = False
        self.after_id = None
        self.fireworks_running = False

        self.create_widgets()

    def create_widgets(self):
        # 创建方格按钮
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                btn = tk.Button(self.root, text=self.grid_names[i][j], width=10, height=5)
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
            self.buttons.append(row)

        # 创建选择按钮
        self.select_button = tk.Button(self.root, text="开始/停止", command=self.toggle_random_selection)
        self.select_button.grid(row=self.grid_size, column=0, columnspan=self.grid_size)

        

    def toggle_random_selection(self):
        if self.running:
            # 停止随机选择
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.running = False
            self.show_selected_square()
        else:
            # 开始随机选择
            self.running = True
            self.random_select()

    def random_select(self):
        if not self.running:
            return

        # 重置所有方格的颜色
        for row in self.buttons:
            for btn in row:
                btn.config(bg="SystemButtonFace")

        # 随机选择一个方格
        random_row = random.randint(0, self.grid_size - 1)
        random_col = random.randint(0, self.grid_size - 1)
        self.selected_button = self.buttons[random_row][random_col]

        # 将选择的方格变为红色
        self.selected_button.config(bg="red")

        # 再次调用自己，设置为100毫秒后
        self.after_id = self.root.after(100, self.random_select)
        

    # def get_image(filename,width,height):
    #     im = Image.open(filename).resize((width,height))
    #     return ImageTk.PhotoImage(im)
    
    def show_selected_square(self):
        selected_name = self.selected_button.cget("text")
        popup = tk.Toplevel(self.root)
        popup.title("选择结果")
        
        
        # im_root=Image.open("kafuka.jpg").resize((400,20))
        # canvas.create_image(400,300,image=im_root)        
        label = tk.Label(popup, text=f"选择的方格是: {selected_name}", font=("Helvetica", 16),anchor="center")
        label.pack(padx= 20,pady= 20)
        
       
        canvas = tk.Canvas(popup, width=200, height=20,anchor="center")
        canvas.pack()

        self.fireworks_running = True
        # self.draw_fireworks(canvas)

    # def draw_fireworks(self, canvas):
    #     if not self.fireworks_running:
    #         return

    #     # 清除画布内容
    #     canvas.delete("all")

    #     # 绘制新的烟花点
    #     for _ in range(5):
    #         x = random.randint(50, 350)
    #         y = random.randint(0, 50)
    #         colors = ["red", "yellow", "blue", "green", "purple", "orange"]
    #         color = random.choice(colors)
    #         for _ in range(40):
    #             angle = radians(random.uniform(0, 360))
    #             length = random.uniform(20, 100)
    #             end_x = x + length * cos(angle)
    #             end_y = y + length * sin(angle)
    #             canvas.create_oval(end_x - 1, end_y - 1, end_x + 1, end_y + 1, fill=color, outline=color)

    #     # 再次调用自己，设置为100毫秒后
    #     canvas.after(100, self.draw_fireworks, canvas)

    def stop_fireworks(self):
        self.fireworks_running = False

if __name__ == "__main__":
    root = tk.Tk()

    # 自定义方格名称
    grid_names = [
        ["A1", "A2", "A3", "A4"],
        ["B1", "B2", "B3", "B4"],
        ["C1", "C2", "C3", "C4"],
        ["D1", "D2", "D3", "D4"]
    ]

    app = RandomSelectorApp(root, grid_names)
    root.mainloop()
