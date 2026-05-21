import sys
import threading
import queue
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import os

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# ========== 设置中文字体，解决绘图乱码 ==========
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

# 配置常量
MAX_DISPLAY_POINTS = 500      # 曲线最多显示点数
BAUDRATE = 9600               # 固定波特率
DATA_TIMEOUT = 1              # 串口读超时(秒)
DEFAULT_GAP_THRESHOLD = 5.0   # 默认不连续阈值（秒）
VISUAL_GAP = 0.5              # 折叠后，两段曲线之间保留的视觉间隙（秒），设为0则完全无缝拼接

class SerialDataPlotter:
    """串口数据实时曲线显示与存储上位机"""
    def __init__(self, root):
        self.root = root
        self.root.title("水质参数监测上位机 - 叶绿素/浊度/藻红蛋白")
        self.root.geometry("1200x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 串口相关变量
        self.serial_port = None          # Serial对象
        self.serial_thread = None        # 读取线程
        self.running = False              # 线程运行标志
        self.data_queue = queue.Queue()   # 数据队列(主线程消费)

        # 数据存储(用于曲线显示)
        self.time_data = []          # X轴显示相对时间(秒) —— 已引入空白折叠
        self.chla_data = []          # 叶绿素
        self.turb_data = []          # 浊度
        self.phyco_data = []         # 藻红蛋白
        
        # 内部时间追踪变量
        self.last_recv_time = None   # 上一次收到数据点的绝对时间
        self.current_display_time = 0.0 # 当前X轴的虚拟累计显示时间

        # 曲线显示控制
        self.show_chla = tk.BooleanVar(value=True)
        self.show_turb = tk.BooleanVar(value=True)
        self.show_phyco = tk.BooleanVar(value=True)

        # 间断阈值（秒），用户可调节
        self.discont_threshold = tk.DoubleVar(value=DEFAULT_GAP_THRESHOLD)

        # 文件存储
        self.csv_file = None          # 文件句柄
        self.csv_writer = None
        self.log_filename = None

        # ---------- 创建UI ----------
        self.create_widgets()

        # 初始化matplotlib图形
        self.init_plot()

        # 启动定时器检查数据队列(每50ms)
        self.root.after(50, self.process_queue)

    def create_widgets(self):
        """创建控制面板和显示区域"""
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- 控制面板 ----
        control_frame = ttk.LabelFrame(main_frame, text="串口控制", padding="5")
        control_frame.pack(fill=tk.X, pady=(0,5))

        ttk.Label(control_frame, text="串口号:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
        self.port_combo = ttk.Combobox(control_frame, width=15)
        self.port_combo.grid(row=0, column=1, padx=5, pady=2)
        self.refresh_ports_btn = ttk.Button(control_frame, text="刷新端口", command=self.refresh_ports)
        self.refresh_ports_btn.grid(row=0, column=2, padx=5)

        self.open_btn = ttk.Button(control_frame, text="打开串口", command=self.open_serial)
        self.open_btn.grid(row=0, column=3, padx=10)
        self.close_btn = ttk.Button(control_frame, text="关闭串口", command=self.close_serial, state=tk.DISABLED)
        self.close_btn.grid(row=0, column=4, padx=5)

        self.clear_btn = ttk.Button(control_frame, text="清空曲线", command=self.clear_curve)
        self.clear_btn.grid(row=0, column=5, padx=10)

        self.savefig_btn = ttk.Button(control_frame, text="保存曲线图", command=self.save_plot)
        self.savefig_btn.grid(row=0, column=6, padx=5)

        self.status_label = ttk.Label(control_frame, text="状态: 未连接", foreground="red")
        self.status_label.grid(row=0, column=7, padx=10)

        # ---- 间断阈值设置 ----
        threshold_frame = ttk.Frame(control_frame)
        threshold_frame.grid(row=0, column=8, padx=10)
        ttk.Label(threshold_frame, text="时间断档判定(秒):").pack(side=tk.LEFT)
        self.threshold_spinbox = ttk.Spinbox(
            threshold_frame, from_=0.5, to=60.0, increment=0.5,
            textvariable=self.discont_threshold, width=6
        )
        self.threshold_spinbox.pack(side=tk.LEFT, padx=5)

        # 最新数值显示
        value_frame = ttk.LabelFrame(main_frame, text="实时数值", padding="5")
        value_frame.pack(fill=tk.X, pady=(0,5))

        self.chla_var = tk.StringVar(value="叶绿素: --")
        self.turb_var = tk.StringVar(value="浊度: --")
        self.phyco_var = tk.StringVar(value="藻红蛋白: --")
        ttk.Label(value_frame, textvariable=self.chla_var, font=('Arial', 10)).pack(side=tk.LEFT, padx=15)
        ttk.Label(value_frame, textvariable=self.turb_var, font=('Arial', 10)).pack(side=tk.LEFT, padx=15)
        ttk.Label(value_frame, textvariable=self.phyco_var, font=('Arial', 10)).pack(side=tk.LEFT, padx=15)

        self.file_label = ttk.Label(value_frame, text="未记录文件", foreground="gray")
        self.file_label.pack(side=tk.RIGHT, padx=10)

        # 曲线显示控制
        curve_ctrl_frame = ttk.LabelFrame(main_frame, text="曲线显示", padding="5")
        curve_ctrl_frame.pack(fill=tk.X, pady=(0,5))
        ttk.Checkbutton(curve_ctrl_frame, text="显示叶绿素", variable=self.show_chla, command=self.update_plot).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(curve_ctrl_frame, text="显示浊度", variable=self.show_turb, command=self.update_plot).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(curve_ctrl_frame, text="显示藻红蛋白", variable=self.show_phyco, command=self.update_plot).pack(side=tk.LEFT, padx=10)

        # 曲线显示区域
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.refresh_ports()

    def init_plot(self):
        """初始化曲线样式、标签等"""
        self.ax.set_title("实时水质参数曲线 (长空白已自动折叠)", fontsize=12)
        self.ax.set_xlabel("累积测量有效时间 (秒)", fontsize=10)
        self.ax.set_ylabel("数值", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.6)

        self.line_chla, = self.ax.plot([], [], 'r-', linewidth=1.5, label='叶绿素')
        self.line_turb, = self.ax.plot([], [], 'g-', linewidth=1.5, label='浊度')
        self.line_phyco, = self.ax.plot([], [], 'b-', linewidth=1.5, label='藻红蛋白')
        self.ax.legend(loc='upper right')
        self.ax.set_autoscaley_on(True)

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def open_serial(self):
        """打开串口，启动读取线程和记录文件"""
        port = self.port_combo.get()
        if not port:
            messagebox.showerror("错误", "请选择一个串口号")
            return

        try:
            self.serial_port = serial.Serial(
                port=port, baudrate=BAUDRATE, bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=DATA_TIMEOUT
            )
            self.serial_port.reset_input_buffer()

            # 创建日志文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_filename = f"data_log_{timestamp}.csv"
            self.csv_file = open(self.log_filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Timestamp', 'Chla', 'Turbidity', 'Phycoerythrin'])
            self.csv_file.flush()
            self.file_label.config(text=f"记录文件: {self.log_filename}", foreground="green")

            # 重置数据缓冲和时间追踪状态
            self.time_data.clear()
            self.chla_data.clear()
            self.turb_data.clear()
            self.phyco_data.clear()
            
            self.last_recv_time = None
            self.current_display_time = 0.0

            self.update_plot()

            self.running = True
            self.serial_thread = threading.Thread(target=self.read_serial_thread, daemon=True)
            self.serial_thread.start()

            self.open_btn.config(state=tk.DISABLED)
            self.close_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"状态: 已连接 {port}", foreground="green")
            self.chla_var.set("叶绿素: --")
            self.turb_var.set("浊度: --")
            self.phyco_var.set("藻红蛋白: --")

        except Exception as e:
            messagebox.showerror("串口打开失败", f"无法打开串口 {port}\n错误: {str(e)}")
            self.close_serial()

    def read_serial_thread(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline()
                if line:
                    data_str = line.decode('ascii', errors='ignore').strip()
                    if data_str:
                        values = self.parse_data_string(data_str)
                        if values:
                            recv_time = datetime.now()
                            self.data_queue.put((recv_time, values[0], values[1], values[2]))
            except Exception as e:
                if self.running:
                    print(f"串口读取错误: {e}")
                break

    def parse_data_string(self, s):
        try:
            parts = s.replace(',', ' ').split()
            if len(parts) < 3:
                return None
            return (float(parts[0]), float(parts[1]), float(parts[2]))
        except Exception:
            return None

    def process_queue(self):
        """核心修改：处理队列，支持长空白时间段折叠"""
        try:
            while True:
                data = self.data_queue.get_nowait()
                recv_time, chla, turb, phyco = data

                # ========== 存储到CSV文件（始终记录真实绝对时间戳） ==========
                if self.csv_writer:
                    time_str = recv_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    self.csv_writer.writerow([time_str, chla, turb, phyco])
                    self.csv_file.flush()

                # ========== 更新显示的最新数值 ==========
                self.chla_var.set(f"叶绿素: {chla:.3f}")
                self.turb_var.set(f"浊度: {turb:.3f}")
                self.phyco_var.set(f"藻红蛋白: {phyco:.3f}")

                # ========== 关键逻辑：计算虚拟X轴坐标（折叠空白） ==========
                if self.last_recv_time is None:
                    # 整个运行周期接收到的第一个有效点
                    self.current_display_time = 0.0
                else:
                    # 计算当前点与上一个有效点的真实时间差
                    actual_gap = (recv_time - self.last_recv_time).total_seconds()
                    threshold = self.discont_threshold.get()

                    if actual_gap > threshold:
                        # 判定发生长时间中断（例如停止了10分钟）
                        # 1. 插入 None 虚拟断点，使 Matplotlib 在此处断开线条不连线
                        self.time_data.append(self.current_display_time + 0.001)
                        self.chla_data.append(None)
                        self.turb_data.append(None)
                        self.phyco_data.append(None)

                        # 2. 虚拟X轴只前进一个很小的视觉间隙(如0.5秒)，而不是加上10分钟
                        self.current_display_time += VISUAL_GAP
                    else:
                        # 正常连续采集，虚拟时间轴累加实际流逝的采样间隔
                        self.current_display_time += actual_gap

                # 更新最后接收时间戳
                self.last_recv_time = recv_time

                # 添加真实数据点到显示缓冲
                self.time_data.append(self.current_display_time)
                self.chla_data.append(chla)
                self.turb_data.append(turb)
                self.phyco_data.append(phyco)

                # 限制显示点数以提高渲染性能
                if len(self.time_data) > MAX_DISPLAY_POINTS:
                    self.time_data = self.time_data[-MAX_DISPLAY_POINTS:]
                    self.chla_data = self.chla_data[-MAX_DISPLAY_POINTS:]
                    self.turb_data = self.turb_data[-MAX_DISPLAY_POINTS:]
                    self.phyco_data = self.phyco_data[-MAX_DISPLAY_POINTS:]

                self.update_plot()

        except queue.Empty:
            pass
        self.root.after(50, self.process_queue)

    def update_plot(self):
        if not self.time_data:
            self.line_chla.set_data([], [])
            self.line_turb.set_data([], [])
            self.line_phyco.set_data([], [])
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw_idle()
            return

        self.line_chla.set_data(self.time_data, self.chla_data)
        self.line_turb.set_data(self.time_data, self.turb_data)
        self.line_phyco.set_data(self.time_data, self.phyco_data)

        self.line_chla.set_visible(self.show_chla.get())
        self.line_turb.set_visible(self.show_turb.get())
        self.line_phyco.set_visible(self.show_phyco.get())

        if self.time_data:
            all_vals = []
            if self.show_chla.get():
                all_vals += [v for v in self.chla_data if v is not None]
            if self.show_turb.get():
                all_vals += [v for v in self.turb_data if v is not None]
            if self.show_phyco.get():
                all_vals += [v for v in self.phyco_data if v is not None]

            x_min = min(self.time_data)
            x_max = max(self.time_data)
            x_pad = 0.1 if x_min == x_max else max(0.1, (x_max - x_min) * 0.05)
            self.ax.set_xlim(x_min - x_pad, x_max + x_pad)

            if all_vals:
                y_min, y_max = min(all_vals), max(all_vals)
                y_pad = 0.1 if y_min == y_max else max(0.1, (y_max - y_min) * 0.1)
                self.ax.set_ylim(y_min - y_pad, y_max + y_pad)

        self.canvas.draw_idle()

    def clear_curve(self):
        """清空当前显示的曲线和历史数据"""
        self.time_data.clear()
        self.chla_data.clear()
        self.turb_data.clear()
        self.phyco_data.clear()
        
        # 清空时重置追踪状态
        self.last_recv_time = None
        self.current_display_time = 0.0
        
        self.update_plot()
        self.status_label.config(text="状态: 曲线已清空", foreground="orange")
        self.root.after(1500, lambda: self.status_label.config(
            text=f"状态: {'已连接' if self.serial_port and self.serial_port.is_open else '未连接'}",
            foreground="green" if self.serial_port and self.serial_port.is_open else "red"))

    def save_plot(self):
        if not self.time_data:
            messagebox.showwarning("无数据", "没有数据可保存，请先接收数据")
            return
        filename = f"curve_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            self.figure.savefig(filename, dpi=150, bbox_inches='tight')
            messagebox.showinfo("保存成功", f"曲线图已保存为: {filename}")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存图片: {e}")

    def close_serial(self):
        self.running = False
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except:
                pass
        self.serial_port = None

        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.file_label.config(text="记录已停止", foreground="gray")

        self.open_btn.config(state=tk.NORMAL)
        self.close_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 未连接", foreground="red")

    def on_closing(self):
        self.close_serial()
        self.root.destroy()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    root = tk.Tk()
    try:
        root.iconbitmap(resource_path('icon.ico'))
    except:
        pass
    app = SerialDataPlotter(root)
    root.mainloop()

if __name__ == "__main__":
    main()