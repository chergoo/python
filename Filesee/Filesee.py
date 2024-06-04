from tkinter import Tk, filedialog
from os import path
from datetime import datetime, timezone
import pytz

# 使用Tkinter弹出文件选择对话框
def select_files():
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    file_paths = filedialog.askopenfilename()
    root.destroy()  # 销毁主窗口
    return file_paths

# 选择需要处理的文件
file_paths = select_files()

def convert_unix_seconds_to_time(seconds):
    # 使用 datetime 从 Unix 时间戳创建 datetime 对象,指定为 UTC 时区
    date_time = datetime.fromtimestamp(seconds, tz=pytz.timezone("Asia/Shanghai"))
    # 格式化为可读的时间格式
    return date_time.strftime("%Y-%m-%d %H:%M:%S.%f")

# 获取绝对路径
print("文件路径：",path.abspath(file_paths))

#	返回 path 所指文件的最近访问时间，点击不打开文件就会刷新时间。
atime = path.getatime(file_paths)
a_time = convert_unix_seconds_to_time(atime)
print("最近访问时间：",a_time)

#	返回 path 所指文件的最近修改时间
mtime = path.getmtime(file_paths)
m_time = convert_unix_seconds_to_time(mtime)
print("最近修改时间：",m_time)

#	返回 path 所指文件的创建时间
ctime = path.getctime(file_paths)
c_time = convert_unix_seconds_to_time(ctime)
print("文件创建时间：：",c_time)

#	返回 path 所指文件大小
print("文件大小：",path.getsize(file_paths),"字节")