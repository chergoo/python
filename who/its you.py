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
        # self.grid_size = 4  #创建一个4×4的方格
        self.rows = 4   #创建方格，行数为4
        self.cols = 5   #创建方格，列数为5   
        self.grid_names = grid_names
        self.buttons = []
        self.running = False
        self.after_id = None
        self.fireworks_running = False

        self.create_widgets()

    def create_widgets(self):
        # 创建方格按钮
        # for i in range(4):
        #     row = []
        #     for j in range(5):
        #         btn = tk.Button(self.root, text=self.grid_names[i][j], width=10, height=5)
        #         btn.grid(row=i, column=j, padx=5, pady=5)
        #         row.append(btn)
        #     self.buttons.append(row)
        # 创建按钮并放置在网格中
        # 定义网格尺寸
        
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if i == 0 and j == 2:
                    continue  # 跳过第一排中间的格子
                btn = tk.Button(root, text=self.grid_names[i][j], width=10, height=5)
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
            self.buttons.append(row)
        # 创建选择按钮
        self.select_button = tk.Button(self.root, text="开始/停止", command=self.toggle_random_selection)
        # self.select_button.grid(row=self.grid, column=0, columnspan=self.grid)
        self.select_button.grid(row=self.rows, column=0, columnspan=self.cols)

        

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
         # 检查按钮列表是否为空

        if not self.buttons:
            print("Button list is empty")
            return

        # 重置所有方格的颜色
        for row in self.buttons:
            for btn in row:
                btn.config(bg="SystemButtonFace")

        while True:
        # 随机选择一个方格
            random_row = random.randint(0, self.rows -1)
            random_col = random.randint(0, self.cols -1)
            print(random_row,random_col)
            if random_row != 0 and random_col != 4: #因为中间一个无方格，在选到该处时需重选
                self.selected_button = self.buttons[random_row][random_col]
                # 将选择的方格变为红色
                self.selected_button.config(bg="red")
                break
       
        

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
        ["A1", "A2", "A3", "A4","A5"],
        ["B1", "B2", "B3", "B4","B5"],
        ["C1", "C2", "C3", "C4","C5"],
        ["D1", "D2", "D3", "D4","D5"]
    ]

    app = RandomSelectorApp(root, grid_names)
    root.mainloop()
