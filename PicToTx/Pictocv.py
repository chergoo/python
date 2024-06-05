import cv2
from tkinter import Tk, filedialog

# 使用Tkinter弹出文件选择对话框
def select_files():
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    file_paths = filedialog.askopenfilename()
    root.destroy()  # 销毁主窗口
    return file_paths

# 选择需要处理的文件
image_path = select_files()
print("已选择图片",image_path)

def image_to_ascii(image_path, width=100, height=None):
    # 读取图像
    image = cv2.imread(image_path)
    print(image.shape,"尺寸")
    # 调整图像大小
    if height is None:
        height = int(image.shape[0] * width / image.shape[1])
    resized_image = cv2.resize(image, (width, height))
    
    # 将图像转换为灰度图
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    
    # 定义ASCII字符集
    ascii_chars = 'jrxnuvczXYBMJC@%#*_+=-:,`. '
    # ascii_chars  = 'tfjrxnuvczXYUJCLQ0OZmwqpdbkhao#MW&8%B@$Il!i~+_-?][}{1)(|\\/`^\",:; '

    
    # 计算每个像素点对应的ASCII字符
    ascii_image = ''
    for i in range(gray_image.shape[0]):
        for j in range(gray_image.shape[1]):
            pixel = gray_image[i, j]
            ascii_index = int(pixel / 255 * (len(ascii_chars) - 1))
            ascii_image += ascii_chars[ascii_index]
        ascii_image += '\n'
    
    return ascii_image
 
# 调用函数进行转换   可以在输入参数调整大小，高度不输入的话会自动计算大小
ascii_image = image_to_ascii(image_path, width=200)
# 将最终结果写入文件
with open('.\\cv2-output.txt', 'w') as f: #输出到运行文件夹
    f.writelines(ascii_image)
    print("已经输出文件")
