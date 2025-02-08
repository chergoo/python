#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
import os

class VideoToGifConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("视频转换为GIF")
        
        # 标签显示
        self.file_label = tk.Label(master, text="请选择视频文件：")
        self.file_label.pack(pady=10)
        
        # 按钮来选择文件
        self.select_button = tk.Button(master, text="选择视频文件", command=self.select_file)
        self.select_button.pack(pady=10)
        
        # 显示视频信息
        self.video_info_label = tk.Label(master, text="视频文件信息：")
        self.video_info_label.pack(pady=10)

        self.info_label = tk.Label(master, text="")
        self.info_label.pack(pady=10)

        # 设置开始时间和结束时间
        self.start_time_label = tk.Label(master, text="开始时间 (秒)：")
        self.start_time_label.pack(pady=5)

        self.start_time_entry = tk.Entry(master)
        self.start_time_entry.pack(pady=5)

        self.end_time_label = tk.Label(master, text="结束时间 (秒)：")
        self.end_time_label.pack(pady=5)

        self.end_time_entry = tk.Entry(master)
        self.end_time_entry.pack(pady=5)

        # 默认按钮，默认开始结束时间
        self.set_default_button = tk.Button(master, text="设置默认时间", command=self.set_default_times)
        self.set_default_button.pack(pady=10)

        # 转换按钮
        self.convert_button = tk.Button(master, text="转换为GIF", command=self.convert_to_gif)
        self.convert_button.pack(pady=10)

        # 初始化视频信息和路径
        self.video_path = None
        self.video_duration = None

    def select_file(self):
        """选择视频文件"""
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
        if file_path:
            self.video_path = file_path
            self.load_video_info()

    def load_video_info(self):
        """加载视频信息并显示"""
        if self.video_path:
            video = VideoFileClip(self.video_path)
            self.video_duration = video.duration  # 获取视频时长（秒）
            video.close()

            # 显示视频信息
            video_name = self.video_path.split("/")[-1]  # 提取文件名
            self.info_label.config(text=f"文件名称: {video_name}\n视频时长: {self.video_duration:.2f}秒")

            # 设置默认的开始时间和结束时间
            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(0, "0")  # 默认开始时间为0秒
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(0, str(int(self.video_duration)))  # 默认结束时间为视频时长

    def set_default_times(self):
        """设置默认的开始时间和结束时间"""
        if self.video_duration:
            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(0, "0")  # 默认开始时间为0秒
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(0, str(int(self.video_duration)))  # 默认结束时间为视频时长

    def convert_to_gif(self):
        """将视频转换为GIF并显示输出路径"""
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        try:
            start_time = float(start_time)
            end_time = float(end_time)
            
            if start_time < 0 or end_time > self.video_duration:
                raise ValueError("开始时间或结束时间超出视频范围")

            if start_time >= end_time:
                raise ValueError("结束时间必须大于开始时间")

            # 裁剪视频并保存为GIF
            output_path = self.create_gif(start_time, end_time)
            
            # 弹出显示GIF输出路径
            messagebox.showinfo("转换完成", f"GIF已成功生成！\n输出路径: {output_path}")

        except ValueError as e:
            messagebox.showerror("输入错误", f"输入无效: {e}")

    def create_gif(self, start_time, end_time):
        """根据给定的时间范围生成GIF"""
        clip = VideoFileClip(self.video_path).subclip(start_time, end_time)
        
        # 这里可以设置帧率和分辨率来优化GIF的生成
        frame_rate = 48  # 降低帧率，减少GIF大小和转换时间
        width, height = 640, 360  # 降低分辨率

        # 设置输出路径
        base_name = os.path.basename(self.video_path).split('.')[0]
        output_path = f"{base_name}_output.gif"
        
        # 保存GIF文件，调整帧率和分辨率
        clip.resize(newsize=(width, height)).write_gif(output_path, fps=frame_rate)
        clip.close()

        return output_path

def main():
    root = tk.Tk()
    app = VideoToGifConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
