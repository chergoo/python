import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import threading
import time
import struct
import os

# 导入绘图相关库
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymodbus.client import ModbusSerialClient as ModbusClient

# --- 解决 Matplotlib 中文显示问题 ---
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class ModbusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Modbus RTU 上位机 (CODeq 测量)")
        self.root.geometry("1000x650")

        # --- 内部变量 ---
        self.is_running = False
        self.client = None
        self.data_x = []
        self.data_y = []
        self.start_time = 0
        self.log_file = "measurement_data.txt"

        self.setup_ui()
        
        # 自动刷新串口列表
        self.refresh_ports()

    def setup_ui(self):
        """初始化界面布局"""
        # --- 左侧控制面板 ---
        ctrl_frame = ttk.LabelFrame(self.root, text="设置与控制", padding=10)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 串口选择
        ttk.Label(ctrl_frame, text="串口端口:").grid(row=0, column=0, sticky="w")
        self.port_combo = ttk.Combobox(ctrl_frame, width=15)
        self.port_combo.grid(row=1, column=0, pady=5)
        
        ttk.Button(ctrl_frame, text="刷新串口", command=self.refresh_ports).grid(row=2, column=0, pady=2)

        # 测量参数
        ttk.Label(ctrl_frame, text="测量间隔 (秒):").grid(row=3, column=0, sticky="w", pady=(15,0))
        self.interval_entry = ttk.Entry(ctrl_frame, width=17)
        self.interval_entry.insert(0, "2.0")
        self.interval_entry.grid(row=4, column=0, pady=5)

        ttk.Label(ctrl_frame, text="设备站号 (Slave ID):").grid(row=5, column=0, sticky="w")
        self.slave_id_entry = ttk.Entry(ctrl_frame, width=17)
        self.slave_id_entry.insert(0, "2")
        self.slave_id_entry.grid(row=6, column=0, pady=5)

        # 状态显示
        ttk.Separator(ctrl_frame, orient='horizontal').grid(row=7, column=0, sticky="ew", pady=20)
        ttk.Label(ctrl_frame, text="当前 CODeq 值:").grid(row=8, column=0, sticky="w")
        self.val_label = tk.Label(ctrl_frame, text="0.000", font=("Helvetica", 32, "bold"), fg="#0078D7")
        self.val_label.grid(row=9, column=0, pady=10)

        # 控制按钮
        self.btn_start = tk.Button(ctrl_frame, text="开始测量", bg="#28a745", fg="white", 
                                  font=("微软雅黑", 12, "bold"), command=self.toggle_measure)
        self.btn_start.grid(row=10, column=0, pady=10, sticky="ew")

        ttk.Button(ctrl_frame, text="清空曲线", command=self.clear_chart).grid(row=11, column=0, pady=5, sticky="ew")
        
        # 底部版权或提示
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(ctrl_frame, textvariable=self.status_var, fg="gray").grid(row=12, column=0, pady=20)

        # --- 右侧绘图区域 ---
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.ax.set_title("CODeq 实时测量曲线")
        self.ax.set_xlabel("相对时间 (s)")
        self.ax.set_ylabel("测量值 (mg/L)")
        self.ax.grid(True, linestyle=':', alpha=0.7)
        
        self.line, = self.ax.plot([], [], 'r-', linewidth=2, label="CODeq")
        self.ax.legend(loc="upper right")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_ports(self):
        """获取并刷新当前可用串口列表"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def toggle_measure(self):
        """切换开始/停止状态"""
        if not self.is_running:
            self.start_measurement()
        else:
            self.stop_measurement()

    def start_measurement(self):
        port = self.port_combo.get()
        if not port:
            messagebox.showwarning("警告", "请先选择一个串口端口")
            return

        try:
            # 初始化 Modbus 客户端
            self.client = ModbusClient(
                port=port,
                baudrate=9600,
                parity='N',
                stopbits=1,
                bytesize=8,
                timeout=1
            )
            
            if not self.client.connect():
                raise Exception(f"无法打开端口 {port}")

            self.is_running = True
            self.btn_start.config(text="停止测量", bg="#dc3545")
            self.status_var.set("正在测量...")
            self.start_time = time.time()
            
            # 开启后台线程进行循环读取
            thread = threading.Thread(target=self.measurement_worker, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("连接错误", str(e))

    def stop_measurement(self):
        self.is_running = False
        if self.client:
            self.client.close()
        self.btn_start.config(text="开始测量", bg="#28a745")
        self.status_var.set("停止中...")

    def measurement_worker(self):
        """后台线程执行的具体 Modbus 通信逻辑"""
        try:
            slave_id = int(self.slave_id_entry.get())
            interval = float(self.interval_entry.get())
        except ValueError:
            slave_id = 0x02
            interval = 2.0

        while self.is_running:
            try:
                # 1. 激发测量 (02 06 00 01 01 01)
                self.client.write_register(address=0x0001, value=0x0101, slave=slave_id)
                
                # 等待传感器测量并转换完成
                time.sleep(1.0) 

                # 2. 查询 CODeq (02 03 03 EA 00 02)
                # 0x03EA = 1002
                response = self.client.read_holding_registers(address=0x03EA, count=2, slave=slave_id)
                
                if not response.isError():
                    # 3. 转换 IEEE 754 浮点数 (大端序)
                    raw_bytes = struct.pack('>HH', response.registers[0], response.registers[1])
                    float_val = struct.unpack('>f', raw_bytes)[0]
                    
                    # 4. 更新数据
                    current_rel_time = time.time() - self.start_time
                    self.process_new_data(current_rel_time, float_val)
                else:
                    self.status_var.set("读取数据失败")
                
                # 等待剩余的间隔时间
                time.sleep(max(0.1, interval - 1.0))
                
            except Exception as e:
                print(f"通信线程异常: {e}")
                break
        
        self.status_var.set("测量已停止")

    def process_new_data(self, t, v):
        """在主线程中安全地更新 UI 和图表"""
        # 保存到文本文件
        try:
            with open(self.log_file, "a") as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp}, {v:.3f}\n")
        except:
            pass

        # 更新绘图数据列表
        self.data_x.append(t)
        self.data_y.append(v)
        
        # 限制数据显示数量，防止绘图点过多导致卡顿 (保留最近500个点)
        if len(self.data_x) > 500:
            self.data_x.pop(0)
            self.data_y.pop(0)

        # 使用 root.after 确保 UI 更新在主线程执行
        self.root.after(0, self.update_ui_elements, t, v)

    def update_ui_elements(self, t, v):
        """真正更新 UI 组件"""
        self.val_label.config(text=f"{v:.3f}")
        
        # 更新曲线数据
        self.line.set_data(self.data_x, self.data_y)
        
        # 动态调整坐标轴刻度
        self.ax.relim()
        self.ax.autoscale_view()
        
        # 重新绘制画布
        self.canvas.draw()

    def clear_chart(self):
        """清空当前图表数据"""
        self.data_x = []
        self.data_y = []
        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.val_label.config(text="0.000")

if __name__ == "__main__":
    root = tk.Tk()
    # # 针对高 DPI 屏幕的清晰度优化 (Windows)
    # try:
    #     from ctypes import windll
    #     windll.shcore.SetProcessDpiAwareness(1)
    # except:
    #     pass
        
    app = ModbusApp(root)
    root.mainloop()