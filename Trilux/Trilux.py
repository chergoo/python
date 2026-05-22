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
MAX_DISPLAY_POINTS = 500      # 单次视窗最多显示点数（不再裁剪历史数据）
BAUDRATE = 9600               # 固定波特率
DATA_TIMEOUT = 1              # 串口读超时(秒)
DEFAULT_GAP_THRESHOLD = 5.0   # 默认不连续阈值（秒）
VISUAL_GAP = 1.0              # 折叠后，两段曲线之间保留的视觉间隙（秒）

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
        self.time_data = []          # X轴虚拟显示相对时间(秒) —— 默认折叠
        self.chla_data = []          # 叶绿素
        self.turb_data = []          # 浊度
        self.phyco_data = []         # 藻红蛋白
        
        # 内部时间追踪变量
        self.last_recv_time = None   # 上一次收到数据点的绝对时间
        self.current_display_time = 0.0 # 当前X轴的虚拟累计显示时间
        self.last_measurement_time = None  # 最近一次成功收到数据的真实时间（用于空白时显示）

        # 存储动态创建的断档标注对象（用于控制隐藏和擦除）
        self.gap_lines = []          # 存储垂直虚线对象
        self.gap_texts = []          # 存储文本标签对象

        # 曲线显示控制
        self.show_chla = tk.BooleanVar(value=True)
        self.show_turb = tk.BooleanVar(value=True)
        self.show_phyco = tk.BooleanVar(value=True)
        
        # 新增：是否显示暂停时间标识（默认开启）
        self.show_gap_time = tk.BooleanVar(value=True)

        # 历史回溯：跟随最新 & 滑块（在 create_widgets 中创建控件）
        self.follow_latest = None   # BooleanVar，create_widgets 中初始化
        self.slider_var = None      # IntVar，create_widgets 中初始化

        # 间断判定阈值（秒）
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
        # 启动空闲时间刷新定时器(每秒更新上次测量时间显示)
        self.root.after(1000, self.update_idle_display)

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

        # 间断阈值设置
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

        # 上次测量时间标签（空白时显示）
        self.last_time_var = tk.StringVar(value="上次测量: --")
        self.last_time_label = ttk.Label(value_frame, textvariable=self.last_time_var,
                                         font=('Arial', 10), foreground="gray")
        self.last_time_label.pack(side=tk.LEFT, padx=20)

        self.file_label = ttk.Label(value_frame, text="未记录文件", foreground="gray")
        self.file_label.pack(side=tk.RIGHT, padx=10)

        # 曲线显示控制区域
        curve_ctrl_frame = ttk.LabelFrame(main_frame, text="曲线显示控制", padding="5")
        curve_ctrl_frame.pack(fill=tk.X, pady=(0,5))
        ttk.Checkbutton(curve_ctrl_frame, text="显示叶绿素", variable=self.show_chla, command=self.update_plot).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(curve_ctrl_frame, text="显示浊度", variable=self.show_turb, command=self.update_plot).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(curve_ctrl_frame, text="显示藻红蛋白", variable=self.show_phyco, command=self.update_plot).pack(side=tk.LEFT, padx=10)
        
        # 新增：控制是否显示暂停时间的复选框
        ttk.Checkbutton(curve_ctrl_frame, text="显示暂停时间", variable=self.show_gap_time, command=self.update_plot).pack(side=tk.RIGHT, padx=15)

        # 曲线显示区域
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ---- 历史回溯导航栏 ----
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(2, 0))

        self.follow_latest = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            nav_frame, text="📌 跟随最新数据",
            variable=self.follow_latest, command=self.on_follow_toggle
        ).pack(side=tk.LEFT, padx=8)

        ttk.Label(nav_frame, text="历史回溯:").pack(side=tk.LEFT, padx=(10, 2))
        self.slider_var = tk.IntVar(value=0)
        self.x_slider = ttk.Scale(
            nav_frame, from_=0, to=0, orient=tk.HORIZONTAL,
            variable=self.slider_var, command=self.on_slider_move
        )
        self.x_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.x_slider.state(['disabled'])   # 初始跟随最新时禁用滑块

        self.slider_pos_label = ttk.Label(nav_frame, text="显示: 最新数据", width=22)
        self.slider_pos_label.pack(side=tk.LEFT, padx=5)

        self.refresh_ports()

    def init_plot(self):
        """初始化曲线样式"""
        self.ax.set_title("实时水质参数监测 (长空白已自动折叠)", fontsize=12)
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
            self._clear_annotations()  # 清除旧图表残留的标注

            self.update_plot()

            self.running = True
            self.serial_thread = threading.Thread(target=self.read_serial_thread, daemon=True)
            self.serial_thread.start()

            self.open_btn.config(state=tk.DISABLED)
            self.close_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"状态: 已连接 {port}", foreground="green")

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
            # 已修复之前遗留的语法错误
            return (float(parts[0]), float(parts[1]), float(parts[2]))
        except Exception:
            return None

    def process_queue(self):
        """核心逻辑：处理队列，计算虚拟X轴，并按需添加精简标注"""
        try:
            while True:
                data = self.data_queue.get_nowait()
                recv_time, chla, turb, phyco = data

                if self.csv_writer:
                    time_str = recv_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    self.csv_writer.writerow([time_str, chla, turb, phyco])
                    self.csv_file.flush()

                self.chla_var.set(f"叶绿素: {chla:.3f}")
                self.turb_var.set(f"浊度: {turb:.3f}")
                self.phyco_var.set(f"藻红蛋白: {phyco:.3f}")

                # 记录本次测量的真实时间
                self.last_measurement_time = recv_time
                self.last_time_label.config(foreground="gray")

                # 计算虚拟 X 轴
                if self.last_recv_time is None:
                    self.current_display_time = 0.0
                else:
                    actual_gap = (recv_time - self.last_recv_time).total_seconds()
                    threshold = self.discont_threshold.get()

                    if actual_gap > threshold:
                        # 1. 插入 None 断点
                        self.time_data.append(self.current_display_time + 0.001)
                        self.chla_data.append(None)
                        self.turb_data.append(None)
                        self.phyco_data.append(None)

                        # 计算断开的确切时间，并转换为短字符串（如 10m0s 或 45s）
                        gap_min, gap_sec = divmod(int(actual_gap), 60)
                        if gap_min > 0:
                            gap_text = f"{gap_min}m{gap_sec}s"
                        else:
                            gap_text = f"{gap_sec}s"

                        # 2. 在画布断裂中央位置初始化垂直标识虚线
                        mid_x = self.current_display_time + (VISUAL_GAP / 2)
                        v_line = self.ax.axvline(x=mid_x, color='#999999', linestyle=':', linewidth=1.0)
                        
                        # 3. 初始化精简文本标签（固定在图表顶部附近 0.94 处）
                        t_anno = self.ax.text(
                            x=mid_x, y=0.94, s=gap_text, color='#666666', fontsize=8,
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax.get_xaxis_transform(),
                            bbox=dict(facecolor='#FFFFFF', alpha=0.8, edgecolor='#DDDDDD', boxstyle='round,pad=0.15')
                        )
                        
                        # 根据当前的勾选状态设定初始可见性
                        v_line.set_visible(self.show_gap_time.get())
                        t_anno.set_visible(self.show_gap_time.get())

                        # 分别存入列表
                        self.gap_lines.append(v_line)
                        self.gap_texts.append(t_anno)

                        # 4. 虚拟时间轴向前推移一个固定视觉间隙
                        self.current_display_time += VISUAL_GAP
                    else:
                        self.current_display_time += actual_gap

                self.last_recv_time = recv_time

                # 将数据加入显示队列
                self.time_data.append(self.current_display_time)
                self.chla_data.append(chla)
                self.turb_data.append(turb)
                self.phyco_data.append(phyco)

                self.update_plot()

        except queue.Empty:
            pass
        self.root.after(50, self.process_queue)

    def update_idle_display(self):
        """每秒刷新一次"上次测量时间"标签，空白时显示距上次的间隔"""
        if self.last_measurement_time is not None:
            time_str = self.last_measurement_time.strftime("%H:%M:%S")
            elapsed = (datetime.now() - self.last_measurement_time).total_seconds()

            # 串口正在接收数据时（间隔 < 阈值），标签显示为灰色普通文字
            # 超过阈值视为空白，用橙色突出显示距上次的秒数
            threshold = self.discont_threshold.get()
            if elapsed < threshold:
                self.last_time_var.set(f"上次测量: {time_str}")
                self.last_time_label.config(foreground="gray")
            else:
                # 将间隔格式化为可读字符串
                idle_min, idle_sec = divmod(int(elapsed), 60)
                idle_hour, idle_min = divmod(idle_min, 60)
                if idle_hour > 0:
                    idle_str = f"{idle_hour}h{idle_min}m{idle_sec}s"
                elif idle_min > 0:
                    idle_str = f"{idle_min}m{idle_sec}s"
                else:
                    idle_str = f"{idle_sec}s"
                self.last_time_var.set(f"上次测量: {time_str}  (已空闲 {idle_str})")
                self.last_time_label.config(foreground="orange")
        else:
            self.last_time_var.set("上次测量: --")
            self.last_time_label.config(foreground="gray")

        self.root.after(1000, self.update_idle_display)

    def on_follow_toggle(self):
        """切换"跟随最新数据"模式"""
        if self.follow_latest.get():
            self.x_slider.state(['disabled'])
            self.slider_pos_label.config(text="显示: 最新数据")
        else:
            self.x_slider.state(['!disabled'])
        self.update_plot()

    def on_slider_move(self, _=None):
        """滑块拖动时刷新视图"""
        if not self.follow_latest.get():
            self.update_plot()

    def update_plot(self):
        """刷新图表：根据滑块/跟随模式选取显示窗口"""
        # 同步所有暂停标注的可见性
        is_visible = self.show_gap_time.get()
        for line in self.gap_lines:
            line.set_visible(is_visible)
        for txt in self.gap_texts:
            txt.set_visible(is_visible)

        total = len(self.time_data)

        if total == 0:
            self.line_chla.set_data([], [])
            self.line_turb.set_data([], [])
            self.line_phyco.set_data([], [])
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw_idle()
            return

        # 更新滑块范围
        max_start = max(0, total - MAX_DISPLAY_POINTS)
        self.x_slider.config(to=max_start)

        # 确定视窗起点
        if self.follow_latest.get():
            start_idx = max_start
            self.slider_var.set(start_idx)
        else:
            start_idx = min(int(self.slider_var.get()), max_start)

        end_idx = min(total, start_idx + MAX_DISPLAY_POINTS)

        # 切片显示数据
        t_view    = self.time_data[start_idx:end_idx]
        chla_view = self.chla_data[start_idx:end_idx]
        turb_view = self.turb_data[start_idx:end_idx]
        phyco_view = self.phyco_data[start_idx:end_idx]

        # 更新滑块位置标签
        if self.follow_latest.get():
            self.slider_pos_label.config(text="显示: 最新数据")
        else:
            pct = int(start_idx / max_start * 100) if max_start > 0 else 100
            self.slider_pos_label.config(
                text=f"第{start_idx+1}~{end_idx}点 ({pct}%)"
            )

        self.line_chla.set_data(t_view, chla_view)
        self.line_turb.set_data(t_view, turb_view)
        self.line_phyco.set_data(t_view, phyco_view)

        self.line_chla.set_visible(self.show_chla.get())
        self.line_turb.set_visible(self.show_turb.get())
        self.line_phyco.set_visible(self.show_phyco.get())

        if t_view:
            all_vals = []
            if self.show_chla.get():
                all_vals += [v for v in chla_view if v is not None]
            if self.show_turb.get():
                all_vals += [v for v in turb_view if v is not None]
            if self.show_phyco.get():
                all_vals += [v for v in phyco_view if v is not None]

            x_min, x_max = min(t_view), max(t_view)
            x_pad = 0.1 if x_min == x_max else max(0.1, (x_max - x_min) * 0.05)
            self.ax.set_xlim(x_min - x_pad, x_max + x_pad)

            if all_vals:
                y_min, y_max = min(all_vals), max(all_vals)
                y_pad = 0.1 if y_min == y_max else max(0.1, (y_max - y_min) * 0.1)
                self.ax.set_ylim(y_min - y_pad, y_max + y_pad)

        self.canvas.draw_idle()

    def _clear_annotations(self):
        """彻底移除图表上的所有标注对象"""
        for line in self.gap_lines:
            try: line.remove()
            except: pass
        for txt in self.gap_texts:
            try: txt.remove()
            except: pass
        self.gap_lines.clear()
        self.gap_texts.clear()

    def clear_curve(self):
        """清空当前显示的曲线、历史数据和标注"""
        self.time_data.clear()
        self.chla_data.clear()
        self.turb_data.clear()
        self.phyco_data.clear()
        
        self.last_recv_time = None
        self.current_display_time = 0.0
        self.last_measurement_time = None
        self.last_time_var.set("上次测量: --")
        self.last_time_label.config(foreground="gray")
        
        self._clear_annotations() # 清空残留标注
        
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