"""
CSV 多文件数据可视化工具
依赖: pip install matplotlib pandas
运行: python csv_plotter.py
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import rcParams
import os

# ── 字体 & 样式 ────────────────────────────────────────────────
rcParams["font.sans-serif"] = ["Microsoft YaHei", "PingFang SC", "Arial Unicode MS", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False

METRICS = ["Chla", "Turbidity", "Phycoerythrin"]
METRIC_LABELS = {
    "Chla": "叶绿素 a (Chla)",
    "Turbidity": "浊度 (Turbidity)",
    "Phycoerythrin": "藻红素 (Phycoerythrin)",
}
COLORS = ["#1D9E75", "#378ADD", "#D85A30", "#7F77DD", "#BA7517",
          "#D4537E", "#3B6D11", "#993C1D", "#185FA5", "#854F0B"]

PLOT_BG   = "#F8F9FA"
AXES_BG   = "#FFFFFF"
GRID_COL  = "#E5E7EB"
TEXT_COL  = "#374151"
PANEL_BG  = "#F1F3F5"
BTN_ACTIVE_BG  = "#E6F1FB"
BTN_ACTIVE_FG  = "#185FA5"
BTN_NORMAL_BG  = "#FFFFFF"
BTN_NORMAL_FG  = "#6B7280"


class CSVPlotter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV 多文件数据可视化")
        self.geometry("1060x700")
        self.configure(bg=PLOT_BG)
        self.minsize(820, 560)

        self.files: dict[str, pd.DataFrame] = {}   # name -> dataframe
        self.active_metric = tk.StringVar(value="Chla")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self._refresh_plot()

    # ── UI 构建 ──────────────────────────────────────────────────
    def _build_ui(self):
        # 顶部控制栏
        top = tk.Frame(self, bg=PLOT_BG, pady=10, padx=14)
        top.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top, text="CSV 多文件可视化", font=("Microsoft YaHei", 13, "bold"),
                 bg=PLOT_BG, fg=TEXT_COL).pack(side=tk.LEFT)

        # 右侧按钮组
        btn_frame = tk.Frame(top, bg=PLOT_BG)
        btn_frame.pack(side=tk.RIGHT)

        self._add_btn = self._make_btn(btn_frame, "＋ 添加文件", self._add_files,
                                       bg="#1D9E75", fg="white", padx=14)
        self._add_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._clear_btn = self._make_btn(btn_frame, "清空", self._clear_files,
                                         bg="#E5E7EB", fg=TEXT_COL, padx=10)
        self._clear_btn.pack(side=tk.LEFT)

        # 指标切换栏
        metric_bar = tk.Frame(self, bg=PANEL_BG, pady=6, padx=14)
        metric_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(metric_bar, text="指标：", font=("Microsoft YaHei", 10),
                 bg=PANEL_BG, fg=TEXT_COL).pack(side=tk.LEFT, padx=(0, 8))

        self._metric_btns = {}
        for m in METRICS:
            b = self._make_btn(metric_bar, m, lambda x=m: self._set_metric(x),
                               bg=BTN_NORMAL_BG, fg=BTN_NORMAL_FG, padx=12, pady=3)
            b.pack(side=tk.LEFT, padx=3)
            self._metric_btns[m] = b
        self._update_metric_btns()

        # 文件列表侧边栏 + 图表主区
        body = tk.Frame(self, bg=PLOT_BG)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(6, 0))

        # 侧边：已加载文件列表
        sidebar = tk.Frame(body, bg=PANEL_BG, width=200,
                           relief=tk.FLAT, bd=0)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="已加载文件", font=("Microsoft YaHei", 10, "bold"),
                 bg=PANEL_BG, fg=TEXT_COL, anchor="w", padx=10, pady=8
                 ).pack(fill=tk.X)

        self._file_list_frame = tk.Frame(sidebar, bg=PANEL_BG)
        self._file_list_frame.pack(fill=tk.BOTH, expand=True, padx=6)

        # 统计区
        self._stats_frame = tk.Frame(sidebar, bg=PANEL_BG)
        self._stats_frame.pack(fill=tk.X, padx=6, pady=(4, 8))

        # 图表区
        chart_area = tk.Frame(body, bg=PLOT_BG)
        chart_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig, self._ax = plt.subplots(figsize=(7.5, 4.5))
        self._fig.patch.set_facecolor(PLOT_BG)
        self._canvas = FigureCanvasTkAgg(self._fig, master=chart_area)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = tk.Frame(chart_area, bg=PLOT_BG)
        toolbar_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(self._canvas, toolbar_frame)

    def _make_btn(self, parent, text, command, bg, fg, padx=8, pady=4):
        b = tk.Button(parent, text=text, command=command,
                      font=("Microsoft YaHei", 9),
                      bg=bg, fg=fg, relief=tk.FLAT,
                      padx=padx, pady=pady, cursor="hand2",
                      activebackground=bg, activeforeground=fg, bd=0)
        return b

    # ── 交互逻辑 ─────────────────────────────────────────────────
    def _on_close(self):
        plt.close("all")
        self.destroy()
        sys.exit(0)

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="选择 CSV 文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        loaded, skipped = 0, 0
        for p in paths:
            name = os.path.basename(p)
            if name in self.files:
                skipped += 1
                continue
            try:
                df = pd.read_csv(p)
                # 标准化列名（去除空格）
                df.columns = [c.strip() for c in df.columns]
                # 确保有需要的列
                missing = [m for m in METRICS if m not in df.columns]
                if missing:
                    messagebox.showwarning("列缺失",
                        f"{name}\n缺少列：{', '.join(missing)}\n已跳过。")
                    continue
                self.files[name] = df
                loaded += 1
            except Exception as e:
                messagebox.showerror("读取失败", f"{name}\n{e}")

        if loaded:
            self._refresh_file_list()
            self._refresh_plot()

    def _clear_files(self):
        self.files.clear()
        self._refresh_file_list()
        self._refresh_plot()

    def _remove_file(self, name):
        self.files.pop(name, None)
        self._refresh_file_list()
        self._refresh_plot()

    def _set_metric(self, m):
        self.active_metric.set(m)
        self._update_metric_btns()
        self._refresh_plot()

    def _update_metric_btns(self):
        cur = self.active_metric.get()
        for m, b in self._metric_btns.items():
            if m == cur:
                b.configure(bg=BTN_ACTIVE_BG, fg=BTN_ACTIVE_FG,
                             font=("Microsoft YaHei", 9, "bold"))
            else:
                b.configure(bg=BTN_NORMAL_BG, fg=BTN_NORMAL_FG,
                             font=("Microsoft YaHei", 9))

    # ── 文件列表刷新 ──────────────────────────────────────────────
    def _refresh_file_list(self):
        for w in self._file_list_frame.winfo_children():
            w.destroy()
        for w in self._stats_frame.winfo_children():
            w.destroy()

        if not self.files:
            tk.Label(self._file_list_frame, text="暂无文件",
                     font=("Microsoft YaHei", 9), bg=PANEL_BG,
                     fg="#9CA3AF").pack(pady=12)
            return

        for i, name in enumerate(self.files):
            color = COLORS[i % len(COLORS)]
            row = tk.Frame(self._file_list_frame, bg=PANEL_BG)
            row.pack(fill=tk.X, pady=2)

            dot = tk.Canvas(row, width=10, height=10, bg=PANEL_BG,
                            highlightthickness=0)
            dot.create_oval(1, 1, 9, 9, fill=color, outline="")
            dot.pack(side=tk.LEFT, padx=(0, 5), pady=3)

            short = name if len(name) <= 22 else name[:19] + "…"
            tk.Label(row, text=short, font=("Microsoft YaHei", 8),
                     bg=PANEL_BG, fg=TEXT_COL, anchor="w"
                     ).pack(side=tk.LEFT, expand=True, fill=tk.X)

            rm = tk.Button(row, text="✕", font=("Arial", 8),
                           bg=PANEL_BG, fg="#9CA3AF", relief=tk.FLAT,
                           bd=0, padx=2, cursor="hand2",
                           command=lambda n=name: self._remove_file(n))
            rm.pack(side=tk.RIGHT)

        # 统计
        metric = self.active_metric.get()
        tk.Label(self._stats_frame,
                 text=f"统计 ({metric})",
                 font=("Microsoft YaHei", 9, "bold"),
                 bg=PANEL_BG, fg=TEXT_COL, anchor="w"
                 ).pack(fill=tk.X, pady=(8, 4))

        for i, (name, df) in enumerate(self.files.items()):
            vals = pd.to_numeric(df[metric], errors="coerce").dropna()
            if vals.empty:
                continue
            color = COLORS[i % len(COLORS)]
            short = name[:18] + "…" if len(name) > 20 else name

            stat_box = tk.Frame(self._stats_frame, bg="#FFFFFF",
                                relief=tk.FLAT, bd=0,
                                highlightbackground="#E5E7EB",
                                highlightthickness=1)
            stat_box.pack(fill=tk.X, pady=3)

            hdr = tk.Frame(stat_box, bg="#FFFFFF")
            hdr.pack(fill=tk.X, padx=8, pady=(5, 2))
            dot2 = tk.Canvas(hdr, width=8, height=8, bg="#FFFFFF",
                             highlightthickness=0)
            dot2.create_oval(0, 0, 8, 8, fill=color, outline="")
            dot2.pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(hdr, text=short, font=("Microsoft YaHei", 7),
                     bg="#FFFFFF", fg="#6B7280").pack(side=tk.LEFT)

            grid = tk.Frame(stat_box, bg="#FFFFFF")
            grid.pack(fill=tk.X, padx=8, pady=(0, 6))
            for col_i, (label, val) in enumerate([
                ("最小", f"{vals.min():.3f}"),
                ("均值", f"{vals.mean():.3f}"),
                ("最大", f"{vals.max():.3f}"),
            ]):
                c = tk.Frame(grid, bg="#FFFFFF")
                c.grid(row=0, column=col_i, padx=(0, 8))
                tk.Label(c, text=label, font=("Microsoft YaHei", 7),
                         bg="#FFFFFF", fg="#9CA3AF").pack()
                tk.Label(c, text=val, font=("Consolas", 8, "bold"),
                         bg="#FFFFFF", fg=TEXT_COL).pack()

    # ── 时间不连续处理：在跳变点插入 NaN 断开折线 ────────────────
    @staticmethod
    def _insert_gaps(x: pd.Series, y: pd.Series, factor: float = 5.0):
        """
        计算相邻时间间隔的中位数，凡超过 factor 倍中位数的间隔
        视为不连续，在该位置插入 NaT/NaN，使折线自动断开。
        """
        if len(x) < 2:
            return x, y
        diffs = x.diff().dt.total_seconds().abs()
        median_diff = diffs.median()
        if median_diff == 0:
            return x, y
        gap_mask = diffs > factor * median_diff
        gap_indices = diffs[gap_mask].index
        if gap_indices.empty:
            return x, y

        rows_x, rows_y = [], []
        prev = 0
        for idx in gap_indices:
            loc = x.index.get_loc(idx)
            rows_x.append(x.iloc[prev:loc])
            rows_y.append(y.iloc[prev:loc])
            rows_x.append(pd.Series([pd.NaT], dtype=x.dtype))
            rows_y.append(pd.Series([float("nan")]))
            prev = loc
        rows_x.append(x.iloc[prev:])
        rows_y.append(y.iloc[prev:])
        return pd.concat(rows_x, ignore_index=True), pd.concat(rows_y, ignore_index=True)

    # ── 绘图 ─────────────────────────────────────────────────────
    def _refresh_plot(self):
        ax = self._ax
        ax.clear()
        ax.set_facecolor(AXES_BG)
        ax.grid(True, color=GRID_COL, linewidth=0.7, linestyle="--")
        ax.tick_params(colors=TEXT_COL, labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#D1D5DB")

        metric = self.active_metric.get()
        ax.set_title(METRIC_LABELS[metric], fontsize=11,
                     color=TEXT_COL, pad=10)
        ax.set_xlabel("时间", fontsize=9, color=TEXT_COL)
        ax.set_ylabel(metric, fontsize=9, color=TEXT_COL)

        if not self.files:
            ax.text(0.5, 0.5, "请添加 CSV 文件", transform=ax.transAxes,
                    ha="center", va="center", fontsize=13,
                    color="#9CA3AF")
            self._canvas.draw()
            return

        has_datetime = False
        for i, (name, df) in enumerate(self.files.items()):
            color = COLORS[i % len(COLORS)]
            y = pd.to_numeric(df[metric], errors="coerce")
            label = name.replace(".csv", "")

            if "Timestamp" in df.columns:
                try:
                    x = pd.to_datetime(df["Timestamp"])
                    x, y = self._insert_gaps(x, y)
                    ax.plot(x, y, color=color, linewidth=1.4, label=label)
                    has_datetime = True
                    continue
                except Exception:
                    pass
            # 回退：行索引
            ax.plot(y.values, color=color, linewidth=1.4, label=label)

        if has_datetime:
            self._fig.autofmt_xdate(rotation=30)
        ax.legend(fontsize=8, framealpha=0.9, edgecolor="#E5E7EB",
                  loc="upper right")
        self._fig.tight_layout()
        self._canvas.draw()
        self._refresh_file_list()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    app = CSVPlotter()
    try:
        app.iconbitmap(resource_path('icon.ico'))
    except Exception:
        pass  # 如果找不到文件，忽略
    app.mainloop()
       
if __name__ == "__main__":
    main()