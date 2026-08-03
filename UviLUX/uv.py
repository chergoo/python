#!/usr/bin/env python3
"""
UviLUX 传感器模拟器
- 支持回放日志文件（按原始时间戳发送）
- 支持生成动态数据（正弦波，可调幅度和偏置）
- 可输出到串口或标准输出
"""

import time
import sys
import argparse
import threading
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

try:
    import serial
except ImportError:
    serial = None


# =====================================================================
# 配置
# =====================================================================
DEFAULT_BAUDRATE = 9600
DEFAULT_INTERVAL = 1.0  # 测量数据间隔（秒）


# =====================================================================
# 数据生成器
# =====================================================================
class SensorDataGenerator:
    """生成模拟传感器数据流"""

    def __init__(self, mode="sine", amplitude=0.5, offset=0.0, frequency=0.1):
        """
        :param mode: 'sine', 'random', 'constant'
        :param amplitude: 幅度
        :param offset: 偏置
        :param frequency: 正弦波频率（Hz）
        """
        self.mode = mode
        self.amplitude = amplitude
        self.offset = offset
        self.frequency = frequency
        self.start_time = time.time()
        self._value = 0.0

    def next_value(self) -> float:
        """生成下一个测量值"""
        t = time.time() - self.start_time
        if self.mode == "sine":
            val = self.amplitude * math.sin(2 * math.pi * self.frequency * t) + self.offset
        elif self.mode == "random":
            val = random.uniform(-self.amplitude, self.amplitude) + self.offset
        else:  # constant
            val = self.offset
        return round(val, 3)


# =====================================================================
# 模拟传感器主逻辑
# =====================================================================
class SensorSimulator:
    def __init__(self, output=None, baudrate=DEFAULT_BAUDRATE, interval=DEFAULT_INTERVAL):
        """
        :param output: 输出目标，可以是串口对象、文件对象或 None（标准输出）
        :param baudrate: 波特率（仅对串口有效）
        :param interval: 测量数据发送间隔（秒）
        """
        self.output = output
        self.baudrate = baudrate
        self.interval = interval
        self._running = False

    def send_line(self, line: str):
        """发送一行数据，末尾添加换行符"""
        line = line.strip()
        if self.output is None:
            # 标准输出
            print(line)
        elif hasattr(self.output, "write"):
            # 文件或串口对象
            self.output.write((line + "\r\n").encode("utf-8"))
            self.output.flush()
        else:
            raise ValueError("不支持的输出类型")

    def send_startup_info(self):
        """发送上电信息（与真实传感器一致）"""
        startup_lines = [
            "** UviLux **",
            "218279-003",
            "chelsea Instrument Type - tryptophan",
            "Code Version - 1.8 Aug 18 2025",
            "EHT Coefficients",
            "  400,+2.38899E-03,-1.50322E+00,02207",
            "  450,+8.93553E-04,-1.49508E+00,02485",
            "  500,+3.66655E-04,-1.50835E+00,02763",
            "  550,+1.62080E-04,-1.49385E+00,03041",
            "  600,+7.71686E-05,-1.48843E+00,03319",
        ]
        for line in startup_lines:
            self.send_line(line)
            time.sleep(0.05)  # 模拟串口发送延迟

    def send_measurement(self, value: float):
        """发送一条测量数据，格式: [+-]xxx.xxx,600,00"""
        # 保证三位整数部分，三位小数，带符号
        sign = "-" if value < 0 else "+"
        abs_val = abs(value)
        int_part = int(abs_val)
        frac_part = int(round((abs_val - int_part) * 1000))
        # 格式化: 例如 -001.030
        formatted = f"{sign}{int_part:03d}.{frac_part:03d}"
        line = f"{formatted},600,00"
        self.send_line(line)

    def run_replay(self, filepath: str, speed: float = 1.0):
        """
        回放日志文件模式
        :param filepath: 日志文件路径
        :param speed: 速度倍率（>1 加速）
        """
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        # 解析时间戳和内容
        entries = []
        for raw in lines:
            raw = raw.strip()
            if not raw:
                continue
            # 尝试解析时间戳 [HH:MM:SS.mmm]
            import re
            match = re.match(r"^\[(\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.*)", raw)
            if match:
                ts_str, content = match.groups()
                # 去除乱码前缀（如 퉷뫹뫲），只保留可打印字符
                content = re.sub(r"^[^\x20-\x7E\*一-鿿]+", "", content).strip()
                if content:
                    entries.append((ts_str, content))
            else:
                # 没有时间戳的行直接作为内容，时间戳沿用上一个
                if entries:
                    entries.append((entries[-1][0], raw))
                else:
                    entries.append(("00:00:00.000", raw))

        if not entries:
            print("没有可回放的数据行")
            return

        # 转换为时间对象（相对时间）
        base_time = datetime.strptime(entries[0][0], "%H:%M:%S.%f")
        for i, (ts_str, content) in enumerate(entries):
            dt = datetime.strptime(ts_str, "%H:%M:%S.%f")
            delta = dt - base_time
            entries[i] = (delta.total_seconds(), content)

        # 发送上电信息（通常开头几行是启动信息，但回放时也发送）
        self.send_startup_info()
        time.sleep(0.5)

        # 按时间间隔发送
        last_time = 0.0
        for delta, content in entries:
            if self._running is False:
                break
            wait = delta - last_time
            if wait > 0:
                time.sleep(wait / speed)
            self.send_line(content)
            last_time = delta

    def run_generate(self, mode="sine", amplitude=0.5, offset=-1.0, frequency=0.1, duration=None):
        """
        生成动态测量数据
        :param mode: 'sine', 'random', 'constant'
        :param amplitude: 幅度
        :param offset: 偏置
        :param frequency: 频率（正弦波）
        :param duration: 运行时长（秒），None 表示无限
        """
        # 先发送一次上电信息
        self.send_startup_info()
        time.sleep(0.5)

        gen = SensorDataGenerator(mode, amplitude, offset, frequency)
        start_time = time.time()
        count = 0

        while self._running:
            if duration is not None and (time.time() - start_time) > duration:
                break

            val = gen.next_value()
            self.send_measurement(val)
            count += 1
            # 等待间隔
            time.sleep(self.interval)

        print(f"生成结束，共发送 {count} 条测量数据")

    def stop(self):
        self._running = False


# =====================================================================
# 主入口
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="UviLUX 传感器模拟器")
    parser.add_argument("--port", help="串口号（例如 COM3 或 /dev/ttyUSB0），若未指定则输出到标准输出")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="波特率")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="测量数据发送间隔（秒）")

    subparsers = parser.add_subparsers(dest="mode", required=True, help="运行模式")

    # 回放模式
    replay_parser = subparsers.add_parser("replay", help="回放日志文件")
    replay_parser.add_argument("file", help="日志文件路径")
    replay_parser.add_argument("--speed", type=float, default=1.0, help="回放速度倍率")

    # 生成模式
    gen_parser = subparsers.add_parser("generate", help="生成动态数据")
    gen_parser.add_argument("--mode", choices=["sine", "random", "constant"], default="sine",
                            help="数据模式")
    gen_parser.add_argument("--amplitude", type=float, default=0.5, help="幅度")
    gen_parser.add_argument("--offset", type=float, default=-1.0, help="偏置")
    gen_parser.add_argument("--frequency", type=float, default=0.1, help="正弦波频率（Hz）")
    gen_parser.add_argument("--duration", type=float, default=None, help="运行时长（秒）")

    args = parser.parse_args()

    # 输出目标
    output = None
    if args.port:
        if serial is None:
            print("错误：未安装 pyserial，无法使用串口输出。")
            sys.exit(1)
        try:
            ser = serial.Serial(port=args.port, baudrate=args.baudrate, timeout=0.5)
            output = ser
            print(f"已打开串口 {args.port}，波特率 {args.baudrate}")
        except Exception as e:
            print(f"无法打开串口 {args.port}: {e}")
            sys.exit(1)
    else:
        # 标准输出
        output = None
        print("输出到标准输出 (stdout)")

    simulator = SensorSimulator(output=output, baudrate=args.baudrate, interval=args.interval)

    try:
        simulator._running = True
        if args.mode == "replay":
            simulator.run_replay(args.file, args.speed)
        elif args.mode == "generate":
            simulator.run_generate(
                mode=args.mode,
                amplitude=args.amplitude,
                offset=args.offset,
                frequency=args.frequency,
                duration=args.duration
            )
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        simulator.stop()
        if output and hasattr(output, "close"):
            output.close()


if __name__ == "__main__":
    main()