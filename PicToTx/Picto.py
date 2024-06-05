from tkinter import Tk, filedialog
from PIL import Image
# import PIL.ImageOps
from tqdm import tqdm


# 使用Tkinter弹出文件选择对话框
def select_files():
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    file_paths = filedialog.askopenfilename()
    root.destroy()  # 销毁主窗口
    return file_paths

# 选择需要处理的文件
input_image_path = select_files()
print("已选择图片",input_image_path)

# 定义字符画的字符集
# ASCII_CHAR = 'The tenderness when you bend your head low,Is like a lotus flower too shy to stand the cool blow,"Take care,take care,"The words of parting are such sweet Sayonara!'
# ASCII_CHAR = "tfjrxnuvczXYUJCLQ0OZmwqpdbkhao#MW&8%B@$`^\",:;Il!i~+_-?][}{1)(|\\/* "
ASCII_CHAR = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."," "] #最后一个设置为空格
# CHAR_LIST = ["爱", "友", "平", "和", "希", "望", "梦", "想", "喜", "悦"," "]

# #获取图片大小
def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        return width, height
#获取图片长宽
a,b = get_image_dimensions(input_image_path)
print("图片长宽分别为",a,b)
# 打开图片
image = Image.open(input_image_path)

# 安装图片原来比例调整图片大小
if a >= 100:
    if 500<= a < 1000:
     image = image.resize((a//2,b//2))
    if a < 500:
     image = image.resize((a,b))
    if a>=1000:
     image = image.resize((a//10,b//10))
else:
    image = image.resize((a*10,b*10))


# 将图片转化为灰度图
image = image.convert('L')

image.save('.\\output_image.jpg')
print("灰度图已保存")

#灰度图颜色翻转
# image = PIL.ImageOps.invert(image)
# image.save('C:\\Users\\gchen\\Desktop\\output_image1.jpg')
# image.show()

# 遍历每个像素，并将像素转化为对应的字符
ascii_image = ''
for y in tqdm(range(image.size[1])): #tqdm生成进度条
    for x in range(image.size[0]):
        pixel = image.getpixel((x, y))
        ascii_image += ASCII_CHAR[pixel//25]
        # ascii_image += CHAR_LIST[pixel // (256 // len(CHAR_LIST))]
    ascii_image += '\n'
    # 假设这代码部分需要0.05s，循环执行60次
    # import time
    # time.sleep(0.05)
 
# 将字符图片保存为txt文件
with open('.\\PIL-output_image.txt', 'w') as f:
    f.write(ascii_image)
    print("转化成功")



