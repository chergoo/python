#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import sqlite3
import threading
import time
import datetime
import ctypes
import webbrowser
from pathlib import Path

# Windows 专用
import win32gui
import win32api
import win32ts

# GUI 托盘
import pystray
from PIL import Image, ImageDraw

# Web 服务
from flask import Flask, jsonify, request, render_template_string

# -----------------------------
# 配置
# -----------------------------
DB_PATH = Path.home() / ".workstation_tracker.db"
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 7788

WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8

# 心跳配置
HEARTBEAT_INTERVAL = 10  # 心跳间隔（秒）
SHUTDOWN_THRESHOLD = 300  # 关机检测阈值（秒，5分钟）

# "离开一下"配置
MANUAL_AWAY_GRACE_SECONDS = 5  # 点击后多少秒内不检测键鼠输入，避免点菜单的动作本身被误判为"回来"

# -----------------------------
# 手动"离开一下"状态
# -----------------------------
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_last_input_tick():
    """返回系统最后一次键鼠输入的 tick 值（越大表示越晚发生输入）"""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    return lii.dwTime

manually_away = False          # 是否处于"离开一下"手动状态
_away_trigger_tick = None      # 触发"离开一下"那一刻的最后输入 tick
_away_trigger_time = None      # 触发"离开一下"的本地时间（用于宽限期判断）
_manual_state_lock = threading.Lock()

def mark_away_manual():
    """托盘菜单点击：进入离开状态，之后检测到任意键鼠动作会自动结束"""
    global manually_away, _away_trigger_tick, _away_trigger_time
    with _manual_state_lock:
        if manually_away:
            return  # 已经处于离开状态，忽略重复点击
        manually_away = True
        _away_trigger_tick = get_last_input_tick()
        _away_trigger_time = time.monotonic()
    log_event('manual_away')

def manual_away_watcher():
    """后台线程：一旦检测到点击"离开一下"之后有新的键鼠输入，自动标记回来
    点击后 MANUAL_AWAY_GRACE_SECONDS 秒内不做检测，避免点菜单本身的鼠标移动/点击被误判为"回来"
    """
    global manually_away, _away_trigger_tick, _away_trigger_time
    while True:
        with _manual_state_lock:
            active = manually_away
            trigger_tick = _away_trigger_tick
            trigger_time = _away_trigger_time
        if active:
            in_grace_period = (time.monotonic() - trigger_time) < MANUAL_AWAY_GRACE_SECONDS
            if not in_grace_period:
                current_tick = get_last_input_tick()
                # dwTime 是自开机以来最后一次输入的时间点，只要比触发时更新，说明有新动作
                if current_tick != trigger_tick:
                    with _manual_state_lock:
                        manually_away = False
                        _away_trigger_tick = None
                        _away_trigger_time = None
                    log_event('manual_back')
        time.sleep(1)

# -----------------------------
# 工具函数
# -----------------------------
def get_boot_time():
    """获取系统本次开机的精确时间"""
    millis = ctypes.windll.kernel32.GetTickCount64()
    boot = datetime.datetime.now() - datetime.timedelta(milliseconds=millis)
    return boot.replace(microsecond=0)

def log_event(event_type, ts=None):
    if ts is None:
        ts = datetime.datetime.now().replace(microsecond=0).isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO events (ts, type) VALUES (?, ?)", (ts, event_type))
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # 事件表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            type TEXT
        )
    """)
    # 心跳表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT
        )
    """)
    conn.close()

def save_heartbeat():
    """保存心跳时间戳"""
    ts = datetime.datetime.now().replace(microsecond=0).isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO heartbeat (ts) VALUES (?)", (ts,))
    
    # 清理旧的心跳记录，只保留最近24小时的
    c.execute("DELETE FROM heartbeat WHERE ts < datetime('now', '-1 day')")
    
    conn.commit()
    conn.close()

def get_last_heartbeat():
    """获取最后的心跳时间"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ts FROM heartbeat ORDER BY ts DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def recover_events():
    """基于心跳机制的开关机恢复逻辑"""
    current_boot_ts = get_boot_time().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 获取最后的事件记录
    c.execute("SELECT ts, type FROM events ORDER BY ts DESC LIMIT 1")
    row = c.fetchone()
    
    # 获取最后的心跳时间
    last_heartbeat = get_last_heartbeat()
    
    if row:
        last_ts, last_type = row[0], row[1]
        
        # 如果数据库最后记录早于本次开机时间，说明中间有关机/重启
        if last_ts < current_boot_ts:
            # 如果有心跳记录，使用心跳逻辑判断
            if last_heartbeat:
                last_heartbeat_dt = datetime.datetime.fromisoformat(last_heartbeat)
                current_boot_dt = datetime.datetime.fromisoformat(current_boot_ts)
                time_gap = (current_boot_dt - last_heartbeat_dt).total_seconds()
                
                # 如果心跳时间在阈值内，认为是短暂中断（如休眠/睡眠）
                if time_gap <= SHUTDOWN_THRESHOLD:
                    # 不记录关机事件，只记录本次开机
                    if last_type == 'shutdown':
                        # 如果上次是关机，需要先记录开机
                        pass
                    else:
                        # 直接记录开机
                        c.execute("INSERT INTO events (ts, type) VALUES (?, 'boot')", (current_boot_ts,))
                else:
                    # 超过阈值，认为是关机重启
                    if last_type != 'shutdown':
                        # 使用最后心跳时间作为关机时间（更接近实际关机时间）
                        c.execute("INSERT INTO events (ts, type) VALUES (?, 'shutdown')", (last_heartbeat,))
                    
                    # 记录本次开机
                    c.execute("INSERT INTO events (ts, type) VALUES (?, 'boot')", (current_boot_ts,))
            else:
                # 没有心跳记录，使用保守策略
                if last_type != 'shutdown':
                    c.execute("INSERT INTO events (ts, type) VALUES (?, 'shutdown')", (last_ts,))
                c.execute("INSERT INTO events (ts, type) VALUES (?, 'boot')", (current_boot_ts,))
    else:
        # 数据库为空，直接记录开机
        c.execute("INSERT INTO events (ts, type) VALUES (?, 'boot')", (current_boot_ts,))
    
    conn.commit()
    conn.close()

def heartbeat_worker():
    """心跳工作线程"""
    while True:
        try:
            save_heartbeat()
        except Exception as e:
            # 心跳保存失败，记录错误但继续运行
            print(f"心跳保存失败: {e}")
        
        time.sleep(HEARTBEAT_INTERVAL)

# -----------------------------
# Web 界面 (含统计功能)
# -----------------------------
app = Flask(__name__)

DASHBOARD_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>工位记录看板</title>
  <script src="/static/js/echarts.min.js"></script>
  <style>
    :root {
      --primary: #4361ee;
      --success: #4cc9f0;
      --away: #cbd5e0;
      --bg: #f8f9fa;
      --card: #ffffff;
    }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); padding: 20px; color: #333; }
    .container { max-width: 1000px; margin: 0 auto; }
    .card { background: var(--card); border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 24px; }
    h2, h3 { margin-top: 0; color: #1a202c; }
    
    .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 24px; }
    .stat-box { padding: 20px; border-radius: 12px; color: white; text-align: left; transition: transform 0.2s; }
    .stat-box:hover { transform: translateY(-3px); }
    .stat-label { font-size: 0.9rem; opacity: 0.9; margin-bottom: 8px; }
    .stat-value { font-size: 1.8rem; font-weight: bold; }
    
    .bg-work { background: linear-gradient(135deg, #4361ee, #4895ef); }
    .bg-away { background: linear-gradient(135deg, #94a3b8, #cbd5e0); }
    .bg-total { background: linear-gradient(135deg, #3f37c9, #4361ee); }

    .controls { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
    input[type="date"] { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; outline: none; }
    button { padding: 8px 20px; background: var(--primary); color: white; border: none; border-radius: 6px; cursor: pointer; transition: 0.2s; }
    button:hover { opacity: 0.9; }

    #chart { width: 100%; height: 350px; }
    
    .table-container { max-height: 400px; overflow-y: auto; }
    table { width: 100%; border-collapse: collapse; }
    th { position: sticky; top: 0; background: #fff; z-index: 1; text-align: left; color: #718096; font-weight: 600; }
    th, td { padding: 12px; border-bottom: 1px solid #edf2f7; }
    .tag { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .tag-boot, .tag-unlock, .tag-manual_back { background: #e0e7ff; color: #4361ee; }
    .tag-lock, .tag-shutdown, .tag-manual_away { background: #f1f5f9; color: #64748b; }
  </style>
</head>
<body>
  <div class="container">
    

      <div class="controls">
        <input type="date" id="date-input">
        <button onclick="load()">刷新数据</button>
      </div>
      
      <div id="chart"></div>
    </div>

    <div class="card">
      <h3>明细记录</h3>
      <div class="table-container">
        <table id="log-table">
          <thead><tr><th>时间</th><th>事件类型</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>logger</h2>
      <div class="stats-grid">
        <div class="stat-box bg-work">
          <div class="stat-label">在位时长</div>
          <div class="stat-value" id="work-time">0h 0m</div>
        </div>
        <div class="stat-box bg-away">
          <div class="stat-label">离开时长</div>
          <div class="stat-value" id="away-time">0h 0m</div>
        </div>
        <div class="stat-box bg-total">
          <div class="stat-label">活跃统计</div>
          <div class="stat-value" id="total-time">0h 0m</div>
        </div>
      </div>
  </div>

<script>
function formatDuration(ms) {
    if (!ms && ms !== 0) return '';
    let totalSeconds = Math.floor(ms / 1000);
    let hours = Math.floor(totalSeconds / 3600);
    let minutes = Math.floor((totalSeconds % 3600) / 60);
    let seconds = totalSeconds % 60;
    const parts = [];
    if (hours > 0) parts.push(hours + '小时');
    if (minutes > 0) parts.push(minutes + '分钟');
    // 小于一小时时显示秒数，便于精确查看短时长
    if (hours === 0 && seconds > 0) parts.push(seconds + '秒');
    if (parts.length === 0) return '0秒';
    return parts.join('');
}

function load() {
    let date = document.getElementById('date-input').value;
    fetch('/api/events?date=' + date).then(r => r.json()).then(res => {
        let events = res.events;
        if (events.length === 0) return;

        let chartData = [];
        let workMs = 0, awayMs = 0;
        
        // 1. 处理数据：寻找开机到关机的完整区间
        for (let i = 0; i < events.length - 1; i++) {
            let start = new Date(events[i].ts).getTime();
            let end = new Date(events[i+1].ts).getTime();
            let duration = end - start;
            let type = events[i].type;

            // 逻辑：lock 或 手动"离开一下"状态到下一个状态之间算作"离开区块"
            let isAway = (type === 'lock' || type === 'manual_away');
            
            if (isAway) {
                awayMs += duration;
                chartData.push({
                    name: '离开 (Locked)',
                    value: [0, start, end, duration],
                    itemStyle: { color: '#4472c4' } // 深蓝色块
                });
            } else {
                workMs += duration;
                // 在位期间用浅灰色背景表示
                chartData.push({
                    name: '在位 (Active)',
                    value: [0, start, end, duration],
                    itemStyle: { color: '#f0f0f0' } // 浅灰色背景
                });
            }
        }

        // 更新统计文字
        document.getElementById('work-time').innerText = formatDuration(workMs);
        document.getElementById('away-time').innerText = formatDuration(awayMs);
        document.getElementById('total-time').innerText = formatDuration(workMs + awayMs);

        const chart = echarts.init(document.getElementById('chart'));
        
        // 创建时间轴数据（从当天0点到23:59:59）
        let dayStart = new Date(date + 'T00:00:00').getTime();
        let dayEnd = new Date(date + 'T23:59:59').getTime();
        
        // 基础配置
        let option = {
            backgroundColor: '#ffffff',
            tooltip: {
                // 使用 item 触发器，确保悬停时显示当前单个区间的数据
                trigger: 'item',
                axisPointer: {
                    type: 'cross'
                },
                formatter: function(params) {
                    // params 是被悬停的单点对象
                    let data = params.data || params;
                    // value 格式为 [0, startMs, endMs, durationMs]
                    let val = data.value || data;
                    let name = data.name || params.seriesName || '';
                    let startMs = val[1];
                    let endMs = val[2];
                    let durationMs = val[3] || (endMs - startMs);
                    let startTime = new Date(startMs).toLocaleTimeString();
                    let endTime = new Date(endMs).toLocaleTimeString();
                    let duration = formatDuration(durationMs);
                    return `${name}<br/>${startTime} - ${endTime}<br/>时长: ${duration}`;
                }
            },
            xAxis: {
                type: 'time',
                position: 'bottom',
                axisLine: {
                    lineStyle: {
                        color: '#4472c4',
                        width: 2
                    }
                },
                axisLabel: {
                    formatter: function(value) {
                        return new Date(value).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
                    }
                },
                min: dayStart,
                max: dayEnd,
                splitLine: {
                    show: false
                }
            },
            yAxis: {
                show: false,
                min: -1,
                max: 1
            },
            series: [{
                type: 'custom',
                renderItem: function(params, api) {
                    let start = api.coord([api.value(1), 0]);
                    let end = api.coord([api.value(2), 0]);
                    let height = 40; // 块的高度
                    
                    // 获取样式
                    let itemStyle = api.style();
                    
                    // 绘制矩形
                    return {
                        type: 'rect',
                        shape: {
                            x: start[0],
                            y: start[1] - height/2,
                            width: Math.max(1, end[0] - start[0]), // 最小宽度为1px
                            height: height
                        },
                        style: itemStyle,
                        emphasis: {
                            style: {
                                shadowBlur: 10,
                                shadowColor: 'rgba(0,0,0,0.3)'
                            }
                        }
                    };
                },
                data: chartData
            }]
        };
        
        chart.setOption(option);
        
        // 明细列表渲染
        document.querySelector('#log-table tbody').innerHTML = events.map(e => 
            `<tr><td>${e.ts.split('T')[1].slice(0,8)}</td><td><span class="tag tag-${e.type}">${e.type.toUpperCase()}</span></td></tr>`
        ).reverse().join('');
    });
}
document.getElementById('date-input').value = new Date().toISOString().slice(0,10);
load();
window.addEventListener('resize', () => echarts.getInstanceByDom(document.getElementById('chart'))?.resize());
</script>
</body>
</html>
"""

# -----------------------------
# 后端服务
# -----------------------------
@app.route("/api/events")
def api_events():
    date = request.args.get("date")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ts, type FROM events WHERE ts LIKE ? ORDER BY ts", (f"{date}%",))
    rows = c.fetchall()
    conn.close()
    return jsonify({"events": [{"ts": r[0], "type": r[1]} for r in rows]})

@app.route("/")
def index(): return render_template_string(DASHBOARD_HTML)

# -----------------------------
# 会话监听 & 托盘
# -----------------------------
class SessionWatcher:
    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_WTSSESSION_CHANGE:
            if wparam == WTS_SESSION_LOCK: log_event('lock')
            elif wparam == WTS_SESSION_UNLOCK: log_event('unlock')
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def start(self):
        def _run():
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._wnd_proc
            wc.lpszClassName = "TrackerWatcher"
            classAtom = win32gui.RegisterClass(wc)
            hwnd = win32gui.CreateWindowEx(0, classAtom, "Hidden", 0, 0, 0, 0, 0, 0, 0, 0, None)
            win32ts.WTSRegisterSessionNotification(hwnd, win32ts.NOTIFY_FOR_THIS_SESSION)
            win32gui.PumpMessages()
        threading.Thread(target=_run, daemon=True).start()

# -----------------------------
# 主程序
# -----------------------------
if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 恢复事件（使用心跳机制）
    recover_events()
    
    # 启动会话监听
    SessionWatcher().start()
    
    # 启动心跳线程
    threading.Thread(target=heartbeat_worker, daemon=True).start()

    # 启动"离开一下"自动结束监测线程
    threading.Thread(target=manual_away_watcher, daemon=True).start()
    
    # 启动Web服务
    threading.Thread(target=lambda: app.run(
        host=FLASK_HOST, 
        port=FLASK_PORT, 
        debug=False, 
        use_reloader=False
    ), daemon=True).start()
    
    # 创建托盘图标
    icon = pystray.Icon(
        "Tracker", 
        Image.new('RGB', (64, 64), (30, 144, 255)), 
        "工位统计", 
        menu=pystray.Menu(
            pystray.MenuItem(
                lambda item: "离开中（有动作自动返回）" if manually_away else "离开一下",
                lambda icon, item: mark_away_manual()
            ),
            pystray.MenuItem("打开面板", lambda: webbrowser.open(f"http://{FLASK_HOST}:{FLASK_PORT}")),
            pystray.MenuItem("退出", lambda i, n: os._exit(0))
        )
    )
    
    # 运行托盘程序
    icon.run()