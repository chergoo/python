# script.spec
# -*- mode: python ; coding: utf-8 -*-

# pyinstaller --onefile --noconsole --icon=icon.ico script.py
# --onefile：将所有文件打包成一个独立的 EXE 文件。
# --noconsole：隐藏控制台窗口（适用于 GUI 应用程序）。
# --icon=icon.ico：指定图标文件（替换 icon.ico 为你的图标文件路径）。

# 加密支持，如果需要加密，可以设置相关参数
block_cipher = None

# Analysis 对象用于分析 Python 脚本及其依赖项
a = Analysis(
    ['script.py'],                # 需要打包的脚本文件
    pathex=['.'],                 # 搜索脚本和依赖项的路径
    binaries=[],                  # 需要打包的二进制文件
    datas=[],                     # 需要打包的额外数据文件
    hiddenimports=[],             # 隐藏导入，PyInstaller 无法检测到的模块
    hookspath=[],                 # 钩子脚本的路径
    hooksconfig={},               # 钩子脚本的配置
    runtime_hooks=[],             # 运行时钩子脚本
    excludes=[],                  # 排除的模块
    win_no_prefer_redirects=False,# 如果为 True，则禁用文件重定向
    win_private_assemblies=False, # 如果为 True，则启用私有程序集
    cipher=block_cipher,          # 加密支持
    noarchive=False,              # 如果为 True，则不将 Python 模块打包到一个文件中
)

# PYZ 对象用于创建包含所有 Python 代码的归档文件
pyz = PYZ(
    a.pure,              # 纯 Python 模块
    a.zipped_data,       # 已压缩的 Python 模块数据
    cipher=block_cipher, # 加密支持
)

# EXE 对象用于创建可执行文件
exe = EXE(
    pyz,                       # 使用的 PYZ 对象
    a.scripts,                 # 脚本文件
    [],                        # 额外的脚本
    exclude_binaries=True,     # 如果为 True，则排除二进制文件
    name='script',             # 可执行文件的名称
    debug=False,               # 如果为 True，则启用调试模式
    bootloader_ignore_signals=False, # 如果为 True，则引导程序忽略信号
    strip=False,               # 如果为 True，则从可执行文件中移除调试符号
    upx=True,                  # 如果为 True，则使用 UPX 压缩可执行文件
    upx_exclude=[],            # 排除 UPX 压缩的文件
    runtime_tmpdir=None,       # 运行时临时目录
    console=True,              # 如果为 True，则创建控制台应用程序
)

# COLLECT 对象用于将所有文件收集到一个目录中
coll = COLLECT(
    exe,              # EXE 对象
    a.binaries,       # 二进制文件
    a.zipfiles,       # 压缩文件
    a.datas,          # 数据文件
    strip=False,      # 如果为 True，则从二进制文件中移除调试符号
    upx=True,         # 如果为 True，则使用 UPX 压缩文件
    upx_exclude=[],   # 排除 UPX 压缩的文件
    name='script',    # 收集目录的名称
)
