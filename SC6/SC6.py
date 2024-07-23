#!/usr/bin/env python3
# encoding: utf-8

import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class SerialApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SC6-数据接收和显示")
        self.geometry("800x600")

        # 串口选择框
        self.port_label = ttk.Label(self, text="选择串口:")
        self.port_label.pack(pady=5)

        self.port_combobox = ttk.Combobox(self, state="readonly")
        self.port_combobox.pack(pady=5)
        self.refresh_ports()

        self.connect_button = ttk.Button(self, text="连接", command=self.connect_serial)
        self.connect_button.pack(pady=5)

        # 设备信息显示
        self.device_info_frame = ttk.LabelFrame(self, text="设备信息")
        self.device_info_frame.pack(fill="x", padx=10, pady=10)

        self.device_model_label = ttk.Label(self.device_info_frame, text="设备型号: ")
        self.device_model_label.pack(anchor="w", padx=10, pady=5)
        
        self.device_serial_label = ttk.Label(self.device_info_frame, text="设备序列号: ")
        self.device_serial_label.pack(anchor="w", padx=10, pady=5)
        
        self.date_label = ttk.Label(self.device_info_frame, text="日期: ")
        self.date_label.pack(anchor="w", padx=10, pady=5)
        
        self.time_label = ttk.Label(self.device_info_frame, text="时间: ")
        self.time_label.pack(anchor="w", padx=10, pady=5)
        
        self.depth_label = ttk.Label(self.device_info_frame, text="深度: ")
        self.depth_label.pack(anchor="w", padx=10, pady=5)
        
        self.water_temp_label = ttk.Label(self.device_info_frame, text="水温: ")
        self.water_temp_label.pack(anchor="w", padx=10, pady=5)
        
        self.tilt_label = ttk.Label(self.device_info_frame, text="倾角: ")
        self.tilt_label.pack(anchor="w", padx=10, pady=5)

        # 创建图表显示区
        self.figure = plt.Figure(figsize=(10, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox['values'] = [port.device for port in ports]

    def connect_serial(self):
        selected_port = self.port_combobox.get()
        if selected_port:
            self.ser = serial.Serial(selected_port, 115200, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
            self.start_serial_thread()

    def start_serial_thread(self):
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial_data(self):
        while True:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('ascii').strip()
                data = line.split(',')

                if len(data) >= 40:
                    device_model = data[0]
                    device_serial = data[1]
                    date = data[2]
                    time = data[3]
                    depth = data[6]
                    water_temp = data[7]
                    tilt = data[8]
                    data_412nm = data[9]
                    data_446nm = data[15]
                    data_470nm = data[21]
                    data_520nm = data[27]
                    data_587nm = data[33]
                    data_700nm = data[39]

                    # 更新设备信息
                    self.device_model_label.config(text=f"设备型号: {device_model}")
                    self.device_serial_label.config(text=f"设备序列号: {device_serial}")
                    self.date_label.config(text=f"日期: {date}")
                    self.time_label.config(text=f"时间: {time}")
                    self.depth_label.config(text=f"深度: {depth}")
                    self.water_temp_label.config(text=f"水温: {water_temp}")
                    self.tilt_label.config(text=f"倾角: {tilt}")

                    # 更新图表
                    self.update_plot([data_412nm, data_446nm, data_470nm, data_520nm, data_587nm, data_700nm])

    def update_plot(self, wavelength_data):
        wavelengths = [412, 446, 470, 520, 587, 700]
        self.ax.clear()
        self.ax.plot(wavelengths, wavelength_data, marker='o')
        self.ax.set_title("后向反射")
        self.ax.set_xlabel("波长 (nm)")
        self.ax.set_ylabel("后向反射(1/m/sr)")
        self.canvas.draw()

if __name__ == "__main__":
    app = SerialApp()
    app.mainloop()
