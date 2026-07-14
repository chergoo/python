#!/usr/bin/env python3
"""
File Change Logger (GUI 备注版本)
检测文件夹变动，若未通过 -m 提供备注且有变动，则弹出窗口输入备注。
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# 尝试导入 tkinter（若打包后缺失，给出友好提示）
try:
    import tkinter as tk
    from tkinter import simpledialog
except ImportError:
    tk = None
    simpledialog = None

SNAPSHOT_FILE = ".snapshot.json"
LOG_FILE = "filelog.txt"
IGNORE_PATTERNS = [".snapshot.json", "filelog.txt"]


def get_folder_snapshot(folder_path):
    snapshot = {}
    folder_path = Path(folder_path).resolve()
    for root, dirs, files in os.walk(folder_path):
        # 过滤忽略文件/文件夹
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS and 
                   str(Path(root) / d) not in IGNORE_PATTERNS]
        files = [f for f in files if f not in IGNORE_PATTERNS and 
                 str(Path(root) / f) not in IGNORE_PATTERNS]
        for name in files + dirs:
            full_path = Path(root) / name
            rel_path = str(full_path.relative_to(folder_path)).replace("\\", "/")
            if full_path.is_file():
                stat = full_path.stat()
                snapshot[rel_path] = {"type": "file", "mtime": stat.st_mtime, "size": stat.st_size}
            else:
                snapshot[rel_path] = {"type": "dir", "mtime": 0, "size": 0}
    return snapshot


def compare_snapshots(old, new):
    added = [p for p in new if p not in old]
    removed = [p for p in old if p not in new]
    modified = []
    for p in old.keys() & new.keys():
        if (old[p]["type"] != new[p]["type"] or
            old[p]["mtime"] != new[p]["mtime"] or
            old[p]["size"] != new[p]["size"]):
            modified.append(p)
    return added, removed, modified


def write_log_entry(log_path, folder_path, changes, note=""):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 文件夹: {folder_path}\n")
        added, removed, modified = changes
        if added:   f.write("  新增:\n    " + "\n    ".join(added) + "\n")
        if removed: f.write("  删除:\n    " + "\n    ".join(removed) + "\n")
        if modified: f.write("  修改:\n    " + "\n    ".join(modified) + "\n")
        if note:
            f.write(f"  备注: {note}\n")
        f.write("-" * 60 + "\n")


def popup_get_note(parent=None):
    """
    弹出输入框让用户输入备注，返回输入字符串（若取消或关闭则返回空字符串）
    """
    if tk is None or simpledialog is None:
        return ""  # 无 GUI 环境，直接返回空
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    # 使窗口置顶（可选）
    root.attributes('-topmost', True)
    note = simpledialog.askstring("文件变动备注", "请输入本次变动的备注（可选）：", parent=root)
    root.destroy()
    return note if note is not None else ""


def main():
    parser = argparse.ArgumentParser(description="记录文件夹内文件/文件夹变动（GUI备注版）")
    parser.add_argument("folder", nargs="?", default=".", help="要监视的文件夹路径（默认当前目录）")
    parser.add_argument("-m", "--message", default="", help="自定义备注信息（若提供，则不弹窗）")
    args = parser.parse_args()

    target_folder = Path(args.folder).resolve()
    if not target_folder.is_dir():
        print(f"错误：{target_folder} 不是一个有效的目录")
        sys.exit(1)

    os.chdir(target_folder)
    current_snapshot = get_folder_snapshot(target_folder)

    # ---- 首次运行 ----
    if not os.path.exists(SNAPSHOT_FILE):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"首次记录 - 文件夹: {target_folder}\n")
            f.write(f"时间: {timestamp}\n")
            f.write("-" * 60 + "\n")
        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(current_snapshot, f, indent=2)
        print(f"首次运行，已记录初始状态到 {LOG_FILE}")
        return

    # ---- 读取旧快照 ----
    try:
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            old_snapshot = json.load(f)
    except:
        print("快照文件损坏，请删除后重新运行初始化。")
        sys.exit(1)

    # ---- 比较变动 ----
    added, removed, modified = compare_snapshots(old_snapshot, current_snapshot)
    changes = (added, removed, modified)
    has_changes = any((added, removed, modified))

    if not has_changes:
        print("未检测到任何变动，日志未更新")
        return

    # ---- 获取备注（优先命令行，其次弹窗） ----
    note = args.message if args.message else ""
    if not note:
        # 未提供命令行备注，则弹出输入框
        try:
            note = popup_get_note()
        except Exception as e:
            print(f"弹出窗口失败: {e}，备注将留空")
            note = ""

    # ---- 写入日志并更新快照 ----
    write_log_entry(LOG_FILE, target_folder, changes, note)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(current_snapshot, f, indent=2)

    print(f"变动已记录到 {LOG_FILE}（备注：{note if note else '无'}）")


if __name__ == "__main__":
    main()