#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

class GachaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("抽卡程序")
        
        self.main_label = tk.Label(root, text=" ", font=("Helvetica", 16))
        self.main_label.pack(pady=20)
        
        self.button = tk.Button(root, text="开始抽卡", command=self.start_gacha, font=("Helvetica", 12))
        self.button.pack(pady=10)
        
        self.result_label = tk.Label(root, font=("Helvetica", 16))
        self.result_label.pack(pady=20)
        
        self.result_button = tk.Button(root, text="返回主界面", command=self.back_to_main, state=tk.DISABLED, font=("Helvetica", 12))
        self.result_button.pack(pady=10)
        
        self.load_images()
        self.result_image = None
    
    def load_images(self):
        # Load GIF image for animation
        self.gif_frames = self.load_gif_frames("choose_5.gif")
        
        # Load JPEG images using PIL and convert to PhotoImage
        try:
            self.result_images = {
                "三星角色": self.load_jpeg_to_photoimage("card_1.jpg"),
                "四星武器": self.load_jpeg_to_photoimage("card_2.jpg"),
                "四星角色": self.load_jpeg_to_photoimage("card_3.jpg"),
                "五星武器": self.load_jpeg_to_photoimage("card_4.jpg"),
                "五星角色": self.load_jpeg_to_photoimage("card_5.jpg")
            }
        except IOError as e:
            messagebox.showerror("错误", f"加载 JPEG 文件出错：{e}")
            self.root.quit()
    
    def load_gif_frames(self, filename):
        gif = Image.open(filename)
        frames = []
        try:
            while True:
                frames.append(ImageTk.PhotoImage(gif))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        return frames
    
    def load_jpeg_to_photoimage(self, filename):
        try:
            image = Image.open(filename)
            photo_image = ImageTk.PhotoImage(image)
            return photo_image
        except Exception as e:
            messagebox.showerror("错误", f"打开图片文件出错：{e}")
            self.root.quit()
    
    def start_gacha(self):
        self.main_label.config(text="抽卡中...")
        self.button.config(state=tk.DISABLED)
        
        self.play_gif_animation(0)
    
    def play_gif_animation(self, index):
        if index < len(self.gif_frames):
            self.result_label.config(image=self.gif_frames[index])
            self.root.after(200, self.play_gif_animation, index + 1)
        else:
            self.show_result()

    def show_result(self):
        self.main_label.config(text="抽卡结果")
        result = random.choice(["三星角色", "四星武器", "四星角色","五星角色", "五星武器"])  # 模拟抽卡结果
        self.result_label.config(image=self.result_images[result])
        self.result_button.config(state=tk.NORMAL)
        self.button.config(state=tk.NORMAL)
        self.result_image = self.result_images[result]  # 保存结果图片对象
    
    def back_to_main(self):
        self.main_label.config(text="欢迎来到抽卡程序！")
        self.result_label.config(image="")
        self.result_button.config(state=tk.DISABLED)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = GachaApp(root)
    root.mainloop()
