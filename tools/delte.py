import os
import shutil
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import configparser

# --- 配置和日志 ---
CONFIG_FILE = 'wechat_cleaner_config.ini'
LAST_PATH_KEY = 'last_wechat_path'

def save_last_path(path):
    """保存上次选择的路径到配置文件"""
    config = configparser.ConfigParser()
    config['Settings'] = {LAST_PATH_KEY: path}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def load_last_path():
    """从配置文件加载上次选择的路径"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'Settings' in config and LAST_PATH_KEY in config['Settings']:
        return config['Settings'][LAST_PATH_KEY]
    return "" # 默认空字符串

def clean_directory_contents(directory_path):
    """
    清空指定目录下的所有文件和子目录。
    """
    if not os.path.isdir(directory_path):
        print(f"警告: 目录 '{directory_path}' 不存在或不是一个有效的目录，跳过清理。")
        return

    print(f"正在清空目录: '{directory_path}'...")
    try:
        # 遍历目录下的所有内容
        for item_name in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item_name)
            if os.path.isfile(item_path):
                # 如果是文件，直接删除
                try:
                    os.remove(item_path)
                    # print(f"  - 已删除文件: '{item_path}'") # 可以取消注释查看每个文件的删除情况
                except OSError as e:
                    print(f"  - 无法删除文件 '{item_path}': {e}")
            elif os.path.isdir(item_path):
                # 如果是子目录，递归删除整个子目录
                try:
                    shutil.rmtree(item_path)
                    # print(f"  - 已删除子目录: '{item_path}'") # 可以取消注释查看每个子目录的删除情况
                except OSError as e:
                    print(f"  - 无法删除子目录 '{item_path}': {e}")
        print(f"目录 '{directory_path}' 清空完成。")
    except Exception as e:
        print(f"清空目录 '{directory_path}' 时发生错误: {e}")

# --- 主程序逻辑 ---
def main():
    root = tk.Tk()
    root.withdraw() # 隐藏主窗口

    print("--- 微信文件清理脚本 ---")
    print("警告: 确保微信客户端已完全关闭，否则可能导致数据损坏。")

    # 尝试加载上次的路径
    initial_dir = load_last_path()
    if not os.path.isdir(initial_dir): # 如果上次的路径无效，则设置一个默认的起始搜索路径
        initial_dir = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.isdir(initial_dir): # 如果用户文档目录也不存在
            initial_dir = os.path.expanduser("~")

    messagebox.showinfo(
        "选择微信 FileStorage 目录",
        "请选择您的微信 'FileStorage' 目录。\n\n"
        "通常路径类似:\n"
        "C:\\Users\\您的用户名\\Documents\\WeChat Files\\您的微信ID\\FileStorage"
    )

    # 弹窗让用户选择目录
    wechat_file_storage_path = filedialog.askdirectory(
        title="选择微信 FileStorage 目录",
        initialdir=initial_dir
    )

    if not wechat_file_storage_path:
        messagebox.showinfo("提示", "未选择目录，操作已取消。")
        print("未选择目录，操作已取消。")
        return

    # 检查用户选择的路径是否可能是 FileStorage 目录
    if not wechat_file_storage_path.lower().endswith("filestorage"):
        response = messagebox.askyesno(
            "路径确认",
            f"您选择的目录 '{wechat_file_storage_path}' 似乎不是 'FileStorage' 目录。\n"
            "继续可能导致意外的数据丢失。您确定要以这个目录作为基础进行清理吗？"
        )
        if not response:
            messagebox.showinfo("提示", "目录选择不符，操作已取消。")
            print("目录选择不符，操作已取消。")
            return

    # 保存本次选择的路径
    save_last_path(wechat_file_storage_path)

    # --- 要清理的子文件夹列表 ---
    # 这些是 FileStorage 目录下通常可以安全清理的缓存类文件夹。
    # 请根据您的需求，增删或修改这个列表中的子文件夹名称。
    # 再次提醒：删除 'File', 'Image', 'Video' 或 'MsgAttach' 下的文件会丢失对应内容，请务必谨慎！
    subfolders_to_clean = [
        "Cache",
        "Sns\Cache",
        "Temp",
        "TempFromPhone",
        "MPPageFastLoad",
        "File", # ⚠️ 谨慎：会删除收发文件，可能重要
        "Image", # ⚠️ 谨慎：会删除收发图片，可能重要
        "Video", # ⚠️ 谨慎：会删除收发视频，可能重要
        # "MsgAttach", # ⚠️ 极其危险：这是聊天记录附件核心，强烈建议用微信内置工具清理
    ]

    # 构建完整的待清理目录路径列表
    full_paths_to_clean = []
    for subfolder in subfolders_to_clean:
        full_paths_to_clean.append(os.path.join(wechat_file_storage_path, subfolder))

    print("\n此操作将永久删除以下目录中的所有文件和子文件夹：")
    for folder in full_paths_to_clean:
        print(f"- {folder}")

    confirmation = messagebox.askyesno(
        "确认清理操作",
        f"您已选择目录：{wechat_file_storage_path}\n\n"
        f"此操作将永久删除以下子目录中的所有内容：\n" +
        "\n".join([os.path.basename(p) for p in full_paths_to_clean]) +
        "\n\n您确定要继续吗？"
    )

    if confirmation:
        for folder_path in full_paths_to_clean:
            clean_directory_contents(folder_path)
        messagebox.showinfo("清理完成", "所有指定目录的清理过程已完成。")
        print("\n所有指定目录的清理过程已完成。")
    else:
        messagebox.showinfo("操作取消", "操作已取消。")
        print("操作已取消。")

    root.destroy() # 关闭 tkinter 隐藏窗口


if __name__ == "__main__":
    main()
    time.sleep(2) # 暂停2秒，让用户看到最终消息