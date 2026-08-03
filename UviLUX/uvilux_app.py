#!/usr/bin/env python3
"""
UviLUX 荧光传感器上位机
- 实时显示测量数据折线图
- 显示传感器序列号、校准参数等上电信息
- 原始传感器报文保存为 txt 日志
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import re
import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

# ── 串口支持检测 ─────────────────────────────────────────────
try:
    import serial
    import serial.tools.list_ports

    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    serial = None


# ═══════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════


@dataclass
class SensorInfo:
    """传感器上电信息"""

    serial_number: str = ""
    instrument_type: str = ""
    firmware_version: str = ""
    eht_coefficients: list = field(default_factory=list)  # [(wl, c1, c2, c3), ...]

    def is_complete(self) -> bool:
        return bool(self.serial_number and self.eht_coefficients)

    def reset(self):
        self.serial_number = ""
        self.instrument_type = ""
        self.firmware_version = ""
        self.eht_coefficients.clear()


# ═══════════════════════════════════════════════════════════════
# 串口工作线程
# ═══════════════════════════════════════════════════════════════


class SerialWorker(threading.Thread):
    """后台串口读取线程，将原始行数据放入队列"""

    def __init__(self, port: str, baudrate: int, rx_queue: queue.Queue):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.rx_queue = rx_queue
        self._stop_event = threading.Event()
        self._ser: "serial.Serial | None" = None
        self.connected = False

    def run(self):
        try:
            self._ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5,
            )
            self.connected = True
            self.rx_queue.put(("__CONNECTED__", self.port))

            while not self._stop_event.is_set():
                try:
                    raw = self._ser.readline()
                    if raw:
                        # 尝试多种编码解码，替换无法识别的字节
                        line = raw.decode("utf-8", errors="replace").strip()
                        if line:
                            self.rx_queue.put(("__DATA__", line))
                except serial.SerialException as e:
                    self.rx_queue.put(("__ERROR__", str(e)))
                    self.connected = False
                    break
                except Exception:
                    continue

        except serial.SerialException as e:
            self.rx_queue.put(("__ERROR__", f"无法打开串口 {self.port}: {e}"))
            self.connected = False
        except Exception as e:
            self.rx_queue.put(("__ERROR__", str(e)))
            self.connected = False
        finally:
            self.connected = False
            self.rx_queue.put(("__DISCONNECTED__", self.port))

    def stop(self):
        self._stop_event.set()
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
# 文件回放工作线程（用于无传感器时测试）
# ═══════════════════════════════════════════════════════════════


class FileReplayWorker(threading.Thread):
    """从日志文件回放数据，模拟传感器输出"""

    def __init__(self, filepath: str, rx_queue: queue.Queue, speed: float = 1.0):
        super().__init__(daemon=True)
        self.filepath = filepath
        self.rx_queue = rx_queue
        self.speed = speed  # 回放速度倍率
        self._stop_event = threading.Event()
        self.connected = False

    def run(self):
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            self.connected = True
            self.rx_queue.put(("__CONNECTED__", f"FILE:{self.filepath}"))

            for raw_line in lines:
                if self._stop_event.is_set():
                    break

                # 去除行首的时间戳前缀 [HH:MM:SS.mmm]
                line = raw_line.strip()
                if not line:
                    continue
                # 尝试去掉时间戳前缀
                ts_match = re.match(r"^\[\d{2}:\d{2}:\d{2}\.\d{3}\]", line)
                if ts_match:
                    line = line[ts_match.end():]
                # 去掉可能的前导乱码（非 ASCII 可打印字符）
                line = re.sub(r"^[^\x20-\x7E\*一-鿿]+", "", line)
                line = line.strip()
                if line:
                    self.rx_queue.put(("__DATA__", line))
                    time.sleep(1.0 / self.speed)  # 模拟 1Hz 输出

            self.rx_queue.put(("__EOF__", ""))
            self.connected = False
            self.rx_queue.put(("__DISCONNECTED__", f"FILE:{self.filepath}"))

        except FileNotFoundError:
            self.rx_queue.put(("__ERROR__", f"文件不存在: {self.filepath}"))
            self.connected = False
        except Exception as e:
            self.rx_queue.put(("__ERROR__", str(e)))
            self.connected = False


# ═══════════════════════════════════════════════════════════════
# 数据解析器
# ═══════════════════════════════════════════════════════════════


class DataParser:
    """解析传感器输出行，区分上电信息和测量数据"""

    # 测量数据: +057.957,600,00 或 -001.030,600,00 或 001.030,600,00
    RE_MEASUREMENT = re.compile(r"^([+-]?\d{3}\.\d{3}),(\d+),(\d+)$")

    # EHT 校准系数: 400,+2.38899E-03,-1.50322E+00,02207
    RE_EHT = re.compile(
        r"^\s*(\d+)\s*,\s*([+\-][\d.]+(?:E[+\-]\d+)?)\s*,\s*"
        r"([+\-][\d.]+(?:E[+\-]\d+)?)\s*,\s*(\d+)\s*$"
    )

    # 序列号: 218279-003
    RE_SERIAL = re.compile(r"^\d{6}-\d{3}$")

    def __init__(self):
        self._in_eht_section = False

    def reset(self):
        self._in_eht_section = False

    def parse(self, line: str) -> dict:
        """
        解析一行数据，返回:
          {"type": "info", "key": "...", "value": "..."}
          {"type": "measurement", "value": float, "mode": str, "status": str}
          {"type": "eht", "wavelength": str, "c1": str, "c2": str, "c3": str}
          {"type": "unknown"}
        """
        # ── 测量数据 ──
        m = self.RE_MEASUREMENT.match(line)
        if m:
            return {
                "type": "measurement",
                "value": float(m.group(1)),
                "mode": m.group(2),
                "status": m.group(3),
            }

        # ── EHT 校准系数 ──
        m_eht = self.RE_EHT.match(line)
        if m_eht:
            return {
                "type": "eht",
                "wavelength": m_eht.group(1),
                "c1": m_eht.group(2),
                "c2": m_eht.group(3),
                "c3": m_eht.group(4),
            }

        # ── EHT Coefficients 标记头 ──
        if "EHT" in line.upper() and "COEFFICIENT" in line.upper():
            self._in_eht_section = True
            return {"type": "info", "key": "eht_header", "value": line}

        # ── 序列号 ──
        if self.RE_SERIAL.match(line):
            return {"type": "info", "key": "serial_number", "value": line}

        # ── 仪器类型（包含 "Instrument Type" 的行）──
        if "INSTRUMENT TYPE" in line.upper():
            # 提取 "- " 之后的内容
            value = line
            if "-" in line:
                value = line.split("-", 1)[1].strip()
            return {"type": "info", "key": "instrument_type", "value": value}

        # ── 固件版本 ──
        if "CODE VERSION" in line.upper() or "VERSION" in line.upper():
            value = line
            if "-" in line:
                value = line.split("-", 1)[1].strip()
            return {"type": "info", "key": "firmware_version", "value": value}

        # ── 传感器名称头 ──
        if "UviLux" in line or "UVILUX" in line.upper():
            return {"type": "info", "key": "sensor_name", "value": line.strip("* ")}
        if "chelsea" in line.lower():
            return {"type": "info", "key": "brand", "value": line.strip("* ")}

        # ── 未知行 ──
        return {"type": "unknown", "raw": line}


# ═══════════════════════════════════════════════════════════════
# 主 GUI 应用
# ═══════════════════════════════════════════════════════════════


class App(tk.Tk):
    """UviLUX 上位机主窗口"""

    # 显示最近的 N 个数据点
    MAX_DATA_POINTS = 300
    # GUI 轮询间隔 (ms)
    POLL_INTERVAL = 50

    def __init__(self):
        super().__init__()

        self.title("UviLUX 传感器上位机")
        self.geometry("1100x720")
        self.minsize(900, 600)

        # ── 状态变量 ──
        self.sensor_info = SensorInfo()
        self.parser = DataParser()
        self.rx_queue: queue.Queue = queue.Queue()
        self.worker: "SerialWorker | FileReplayWorker | None" = None

        # 测量数据缓冲
        self.timestamps: deque = deque(maxlen=self.MAX_DATA_POINTS)
        self.measurements: deque = deque(maxlen=self.MAX_DATA_POINTS)

        # 当前测量模式
        self.current_mode: str = "-"

        # 日志文件句柄
        self._log_file = None
        self._log_filename: str = ""

        # 数据计数
        self.data_count: int = 0

        # ── 构建界面 ──
        self._build_ui()

        # ── 启动轮询 ──
        self._poll_queue()

        # ── 窗口关闭处理 ──
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────────────────
    # 界面构建
    # ─────────────────────────────────────────────────────────

    def _build_ui(self):
        # 整体网格布局
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)  # 信息面板
        self.rowconfigure(1, weight=0)  # EHT + 模式
        self.rowconfigure(2, weight=1)  # 图表
        self.rowconfigure(3, weight=0)  # 控制栏
        self.rowconfigure(4, weight=0)  # 状态栏

        self._build_info_panel()
        self._build_eht_and_mode_panel()
        self._build_chart_panel()
        self._build_control_panel()
        self._build_status_bar()

    def _build_info_panel(self):
        """顶部：传感器信息面板"""
        frame = ttk.LabelFrame(self, text="传感器信息", padding=8)
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))

        # 序列号
        ttk.Label(frame, text="序列号:").grid(row=0, column=0, sticky="w")
        self.lbl_serial = ttk.Label(frame, text="-", font=("Consolas", 11, "bold"))
        self.lbl_serial.grid(row=0, column=1, sticky="w", padx=(8, 24))

        # 仪器类型
        ttk.Label(frame, text="仪器类型:").grid(row=0, column=2, sticky="w")
        self.lbl_type = ttk.Label(frame, text="-")
        self.lbl_type.grid(row=0, column=3, sticky="w", padx=(8, 24))

        # 固件版本
        ttk.Label(frame, text="固件版本:").grid(row=0, column=4, sticky="w")
        self.lbl_fw = ttk.Label(frame, text="-")
        self.lbl_fw.grid(row=0, column=5, sticky="w", padx=(8, 8))

    def _build_eht_and_mode_panel(self):
        """中部左侧：EHT 校准系数表格 + 右侧：测量模式"""
        container = ttk.Frame(self)
        container.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=4)

        # ── EHT 校准系数 ──
        eht_frame = ttk.LabelFrame(container, text="EHT 校准系数", padding=4)
        eht_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 表头
        cols = [("波长", 60), ("系数 A", 130), ("系数 B", 130), ("系数 C", 70)]
        self.eht_tree = ttk.Treeview(
            eht_frame, columns=[c[0] for c in cols], show="headings", height=5
        )
        for col, width in cols:
            self.eht_tree.heading(col, text=col)
            self.eht_tree.column(col, width=width, anchor="center")
        self.eht_tree.pack(fill=tk.BOTH, expand=True)

        # ── 测量模式 ──
        mode_frame = ttk.LabelFrame(container, text="测量模式", padding=12)
        mode_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))

        self.lbl_mode_value = ttk.Label(
            mode_frame, text="-", font=("Consolas", 28, "bold")
        )
        self.lbl_mode_value.pack()

        self.lbl_mode_label = ttk.Label(mode_frame, text="Gain")
        self.lbl_mode_label.pack()

        # 当前测量值
        ttk.Separator(mode_frame, orient="horizontal").pack(fill=tk.X, pady=8)
        ttk.Label(mode_frame, text="当前测量值", font=("", 9)).pack()
        self.lbl_current_value = ttk.Label(
            mode_frame, text="-.---", font=("Consolas", 20, "bold")
        )
        self.lbl_current_value.pack()

    def _build_chart_panel(self):
        """中部：matplotlib 实时折线图"""
        chart_frame = ttk.LabelFrame(self, text="实时测量数据", padding=4)
        chart_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        chart_frame.rowconfigure(0, weight=1)
        chart_frame.columnconfigure(0, weight=1)

        # 创建 matplotlib 图表
        self.fig = Figure(figsize=(8, 3.5), dpi=100)
        self.fig.set_tight_layout(True)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("测量值")
        self.ax.set_xlabel("时间")
        self.ax.grid(True, alpha=0.3)
        self.ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")

        # 初始空线
        (self.line_measure,) = self.ax.plot([], [], "b-", linewidth=1.2)

        # 嵌入 tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _build_control_panel(self):
        """底部：串口控制"""
        ctrl_frame = ttk.LabelFrame(self, text="连接控制", padding=6)
        ctrl_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=4)

        # COM 口选择
        ttk.Label(ctrl_frame, text="串口:").pack(side=tk.LEFT)
        self.combo_port = ttk.Combobox(ctrl_frame, width=12, state="readonly")
        self.combo_port.pack(side=tk.LEFT, padx=(4, 8))
        self._refresh_ports()

        # 波特率
        ttk.Label(ctrl_frame, text="波特率:").pack(side=tk.LEFT)
        self.combo_baud = ttk.Combobox(
            ctrl_frame,
            width=10,
            values=["9600", "19200", "38400", "57600", "115200", "230400"],
            state="readonly",
        )
        self.combo_baud.set("9600")
        self.combo_baud.pack(side=tk.LEFT, padx=(4, 16))

        # 连接/断开按钮
        self.btn_connect = ttk.Button(
            ctrl_frame, text="● 连接", command=self._toggle_connect
        )
        self.btn_connect.pack(side=tk.LEFT, padx=4)

        self.btn_disconnect = ttk.Button(
            ctrl_frame, text="断开", command=self._disconnect, state=tk.DISABLED
        )
        self.btn_disconnect.pack(side=tk.LEFT, padx=4)

        # 文件回放按钮
        self.btn_replay = ttk.Button(
            ctrl_frame, text="📁 文件回放", command=self._start_file_replay
        )
        self.btn_replay.pack(side=tk.LEFT, padx=(16, 4))

        # 刷新 COM 口
        ttk.Button(ctrl_frame, text="刷新", command=self._refresh_ports).pack(
            side=tk.LEFT, padx=4
        )

        # 清空图表
        ttk.Button(ctrl_frame, text="清空图表", command=self._clear_chart).pack(
            side=tk.RIGHT, padx=4
        )

    def _build_status_bar(self):
        """底部状态栏"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))

        self.lbl_status = ttk.Label(status_frame, text="状态: 未连接", relief=tk.SUNKEN, padding=(4, 2))
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_count = ttk.Label(status_frame, text="数据: 0 条", relief=tk.SUNKEN, padding=(4, 2))
        self.lbl_count.pack(side=tk.LEFT, padx=(4, 0))

        self.lbl_last = ttk.Label(status_frame, text="最后更新: -", relief=tk.SUNKEN, padding=(4, 2))
        self.lbl_last.pack(side=tk.LEFT, padx=(4, 0))

        self.lbl_log = ttk.Label(status_frame, text="日志: -", relief=tk.SUNKEN, padding=(4, 2))
        self.lbl_log.pack(side=tk.LEFT, padx=(4, 0))

    # ─────────────────────────────────────────────────────────
    # 串口控制
    # ─────────────────────────────────────────────────────────

    def _refresh_ports(self):
        """刷新可用 COM 口列表"""
        if HAS_SERIAL:
            ports = [p.device for p in serial.tools.list_ports.comports()]
        else:
            ports = []
        self.combo_port["values"] = ports
        if ports:
            self.combo_port.set(ports[0])

    def _toggle_connect(self):
        """连接/断开切换"""
        if self.worker and self.worker.is_alive():
            self._disconnect()
        else:
            self._connect_serial()

    def _connect_serial(self):
        """连接串口"""
        if not HAS_SERIAL:
            messagebox.showerror("错误", "未安装 pyserial 库\n请运行: pip install pyserial")
            return

        port = self.combo_port.get()
        if not port:
            messagebox.showwarning("提示", "请先选择串口")
            return

        try:
            baud = int(self.combo_baud.get())
        except ValueError:
            baud = 115200

        self._start_worker(port, baud)

    def _disconnect(self):
        """断开连接"""
        if self.worker:
            self.worker.stop()
        self._set_connected_state(False)

    def _start_worker(self, port, baud=None):
        """启动串口工作线程"""
        self._disconnect()  # 确保之前的连接已关闭
        self._clear_data()

        self.worker = SerialWorker(port, baud or 115200, self.rx_queue)
        self.worker.start()

    def _start_file_replay(self):
        """从文件回放数据"""
        filepath = filedialog.askopenfilename(
            title="选择数据日志文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
        )
        if not filepath:
            return

        self._disconnect()
        self._clear_data()

        self.worker = FileReplayWorker(filepath, self.rx_queue, speed=1.0)
        self.worker.start()

    def _set_connected_state(self, connected: bool):
        """更新连接状态下的 UI"""
        if connected:
            self.btn_connect.configure(state=tk.DISABLED)
            self.btn_disconnect.configure(state=tk.NORMAL)
        else:
            self.btn_connect.configure(state=tk.NORMAL)
            self.btn_disconnect.configure(state=tk.DISABLED)

    def _clear_data(self):
        """清空所有数据缓冲"""
        self.timestamps.clear()
        self.measurements.clear()
        self.data_count = 0
        self.current_mode = "-"
        self.sensor_info.reset()
        self.parser.reset()
        self._update_chart()
        self._update_info_display()
        self._update_mode_display()
        self._update_status()

    def _clear_chart(self):
        """仅清空图表数据"""
        self.timestamps.clear()
        self.measurements.clear()
        self._update_chart()

    # ─────────────────────────────────────────────────────────
    # 队列轮询与数据处理
    # ─────────────────────────────────────────────────────────

    def _poll_queue(self):
        """定时轮询队列，处理来自工作线程的数据"""
        try:
            while True:
                msg = self.rx_queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass
        finally:
            self.after(self.POLL_INTERVAL, self._poll_queue)

    def _handle_message(self, msg: tuple):
        """处理队列消息"""
        msg_type, payload = msg[0], msg[1]

        if msg_type == "__CONNECTED__":
            self._set_connected_state(True)
            self.lbl_status.configure(text=f"状态: 已连接 ({payload})")
            self._open_log_file()

        elif msg_type == "__DISCONNECTED__":
            self._set_connected_state(False)
            self.lbl_status.configure(text="状态: 已断开")
            self._close_log_file()

        elif msg_type == "__DATA__":
            self._process_line(payload)

        elif msg_type == "__ERROR__":
            self.after(0, lambda: messagebox.showerror("串口错误", payload))
            self._set_connected_state(False)
            self.lbl_status.configure(text="状态: 错误")

        elif msg_type == "__EOF__":
            self.lbl_status.configure(text="状态: 文件回放结束")

        elif msg_type == "__SYSMSG__":
            # 系统消息（保留扩展）
            pass

    def _process_line(self, line: str):
        """处理一行原始数据"""
        # ── 写入原始日志 ──
        self._write_log(line)

        # ── 解析数据 ──
        result = self.parser.parse(line)

        if result["type"] == "measurement":
            # 测量数据
            value = result["value"]
            mode = result["mode"]
            # status = result["status"]  # 暂不显示

            now = datetime.now()
            self.timestamps.append(now)
            self.measurements.append(value)
            self.current_mode = mode
            self.data_count += 1

            self._update_chart()
            self._update_mode_display()
            self._update_status()

        elif result["type"] == "eht":
            # 校准系数
            self.sensor_info.eht_coefficients.append(
                (result["wavelength"], result["c1"], result["c2"], result["c3"])
            )
            self._update_eht_table()

        elif result["type"] == "info":
            key = result["key"]
            value = result["value"]
            if key == "serial_number":
                self.sensor_info.serial_number = value
            elif key == "instrument_type":
                self.sensor_info.instrument_type = value
            elif key == "firmware_version":
                self.sensor_info.firmware_version = value
            self._update_info_display()

        # unknown 类型静默忽略

    # ─────────────────────────────────────────────────────────
    # UI 更新方法
    # ─────────────────────────────────────────────────────────

    def _update_info_display(self):
        """更新传感器信息面板"""
        info = self.sensor_info
        self.lbl_serial.configure(text=info.serial_number or "-")
        self.lbl_type.configure(text=info.instrument_type or "-")
        self.lbl_fw.configure(text=info.firmware_version or "-")

    def _update_eht_table(self):
        """更新 EHT 校准系数表格"""
        # 清空旧数据
        for item in self.eht_tree.get_children():
            self.eht_tree.delete(item)
        # 填充新数据
        for wl, c1, c2, c3 in self.sensor_info.eht_coefficients:
            self.eht_tree.insert("", tk.END, values=(wl, c1, c2, c3))

    def _update_mode_display(self):
        """更新测量模式显示"""
        self.lbl_mode_value.configure(text=self.current_mode)
        if self.measurements:
            latest = self.measurements[-1]
            self.lbl_current_value.configure(text=f"{latest:.3f}")

    def _update_chart(self):
        self.ax.cla()
        self.ax.set_ylabel("测量值")
        self.ax.set_xlabel("时间")
        self.ax.grid(True, alpha=0.3)
        self.ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")

        if self.timestamps and self.measurements:
            ts = list(self.timestamps)
            vals = list(self.measurements)
            self.ax.plot(ts, vals, "b-", linewidth=1.2)

            # 标注最新值
            if len(vals) > 0:
                self.ax.annotate(
                    f"{vals[-1]:.3f}",
                    xy=(ts[-1], vals[-1]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                    color="blue",
                )

            # 自动调整轴范围（包括 x 和 y）
            self.ax.relim()
            self.ax.autoscale_view()

            # 设置 x 轴时间格式（定位器自动选择）
            self.ax.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter("%H:%M:%S")
            )
            self.fig.autofmt_xdate()  # 旋转标签，防止重叠

        self.canvas.draw_idle()

    def _update_status(self):
        """更新状态栏"""
        self.lbl_count.configure(text=f"数据: {self.data_count} 条")
        if self.timestamps:
            last_time = self.timestamps[-1].strftime("%H:%M:%S")
            self.lbl_last.configure(text=f"最后更新: {last_time}")

    # ─────────────────────────────────────────────────────────
    # 日志文件
    # ─────────────────────────────────────────────────────────

    def _open_log_file(self):
        """创建新的日志文件"""
        log_dir = os.path.join(os.path.expanduser("~"), "Desktop", "uvilux_data")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_filename = os.path.join(log_dir, f"uvilux_{timestamp}.txt")

        try:
            self._log_file = open(self._log_filename, "w", encoding="utf-8")
            self._log_file.write(
                f"# UviLUX 原始数据日志\n"
                f"# 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"# ==========\n"
            )
            self._log_file.flush()
            self.lbl_log.configure(
                text=f"日志: {os.path.basename(self._log_filename)}"
            )
        except Exception as e:
            print(f"[LOG ERROR] 无法创建日志文件: {e}")
            self._log_file = None

    def _write_log(self, line: str):
        """写入一行到日志文件"""
        if self._log_file:
            try:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self._log_file.write(f"[{ts}] {line}\n")
                self._log_file.flush()
            except Exception:
                pass

    def _close_log_file(self):
        """关闭日志文件"""
        if self._log_file:
            try:
                self._log_file.write(
                    f"# ==========\n"
                    f"# 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                self._log_file.close()
            except Exception:
                pass
            self._log_file = None
            self.lbl_log.configure(text=f"日志: 已保存")

    # ─────────────────────────────────────────────────────────
    # 关闭处理
    # ─────────────────────────────────────────────────────────

    def _on_close(self):
        """窗口关闭时的清理"""
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.worker.join(timeout=1.0)
        self._close_log_file()
        self.destroy()


# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════


def main():
    # 设置中文字体（如果可用）
    try:
        matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
