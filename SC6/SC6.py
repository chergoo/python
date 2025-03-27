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
        
        self.ser = None  # 串口对象
        self.serial_thread = None  # 串口读取线程
        self.is_connected = False  # 连接状态标志
        super().__init__()

        self.title("SC6-数据接收和显示")
        self.geometry("800x600")

        # 串口选择框
        self.port_label = ttk.Label(self, text="选择串口:")
        self.port_label.pack(pady=5)

        self.port_combobox = ttk.Combobox(self, state="readonly")
        self.port_combobox.pack(pady=5)
        self.refresh_ports()

        self.connect_button = ttk.Button(self, text="连接", command=self.toggle_serial_connection)
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

    def toggle_serial_connection(self):
        """切换串口连接状态"""
        if not self.is_connected:
            self.connect_serial()  # 连接串口
        else:
            self.disconnect_serial()  # 断开串口

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox['values'] = [port.device for port in ports]

    def connect_serial(self):
        selected_port = self.port_combobox.get()
        if selected_port:
            try:
                self.ser = serial.Serial(selected_port, 115200, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
                self.is_connected = True
                self.start_serial_thread()
                self.connect_button.config(text="断开", style="Green.TButton")  # 按钮变绿
            except Exception as e:
                print(f"连接失败: {e}")

    def start_serial_thread(self):
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def disconnect_serial(self):
        """断开串口并停止读取线程"""
        if self.ser and self.ser.is_open:
            self.ser.close()  # 关闭串口
        self.is_connected = False
        self.connect_button.config(text="连接", style="Red.TButton")  # 按钮变红

    def read_serial_data(self):
        while self.is_connected:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('ascii').strip()
                data = line.split(',')
                # 将列表元素拼接成字符串，并用空格分隔
                output_string = ' '.join(data)
                with open(f'sc6_data.txt', 'a') as file:
                    file.write(output_string+"\n")
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
    
# 创建主窗口
    
    app = SerialApp()
    head = "ID,SN,DD/MM/YYYY,hh:mm:ss.sss,Flag,Voltage,Depth,TempW,Tilt,Sig[0],Tpcb[0],LEDref[0],Dark[0],LEDval[0],TLED[0],Sig[1],Tpcb[1],LEDref[1],Dark[1],LEDval[1],TLED[1],Sig[2],Tpcb[2],LEDref[2],Dark[2],LEDval[2],TLED[2],Sig[3],Tpcb[3],LEDref[3],Dark[3],LEDval[3],TLED[3],Sig[4],Tpcb[4],LEDref[4],Dark[4],LEDval[4],TLED[4],Sig[5],Tpcb[5],LEDref[5],Dark[5],LEDval[55],TLED[5]"
    with open(f'sc6_data.txt', 'w') as file:
        file.write(head+"\n")
    # 定义按钮样式
style = ttk.Style()
style.configure("Green.TButton", foreground="black", background="green")
style.configure("Red.TButton", foreground="black", background="red")
app.mainloop()
