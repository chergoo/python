import os


def get_folder_size(folder_path):
    """获取文件夹的大小（字节）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def find_folders_and_sizes(root_folder, target_folder_name):
    """遍历根文件夹，查找目标文件夹并输出其路径和大小"""
    st = 0
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for dirname in dirnames:
            if dirname == target_folder_name:
                folder_path = os.path.join(dirpath, dirname)
                folder_size = get_folder_size(folder_path)
                st = float(folder_size / (1024 * 1024))+st
                
                print(f"路径: {folder_path}, 大小: {folder_size / (1024 * 1024):.2f} MB")
    if st > 1024:
        print(f"总大小：{st/1024:.2f}GB")
    else:
        print(f"总大小：{st:.2f}MB")

# 设置根文件夹路径
root_folder = "D:\\"  # 可以根据需要修改根文件夹路径

# 查找并输出名为“发货测试”的文件夹的路径和大小
find_folders_and_sizes(root_folder, "发货测试")