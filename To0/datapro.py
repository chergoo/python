

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import Tk, filedialog
import os


# 使用Tkinter弹出文件选择对话框
def select_files():
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    file_paths = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    root.destroy()  # 销毁主窗口
    return file_paths

# 选择需要处理的CSV文件
file_paths = select_files()

# 读取CSV文件
data = pd.read_csv(file_paths)
# #读取csv文件
# data = pd.read_csv("50C7_1.0.csv")

#打印数据前5行查看数据结构
#print(data.head())

#提取x,y数据
x = data.iloc[0:,0].astype(float) #x为第一列
#y = data.iloc[1:,1].astype(float) #y为第二列

print(x)
# 初始化存储x为0时y值的列表
y_at_zero_list = []

# 初始化存储列名和x为0时y值的字典
results = {'Column': [], 'Y_at_X=0': []}

# 遍历除了第一列以外的每一列数据
for col in data.columns[1:]:
    # 提取y轴数据
    y = data[col].astype(float)

    print(y)
    
    # 进行最小二乘法拟合
    coefficients = np.polyfit(x, y, 2)
    
    # 使用拟合系数创建拟合曲线函数
    fitted_curve = np.poly1d(coefficients)
    
    # 计算拟合曲线在x为0时的y值
    y_at_zero = fitted_curve(0)
    
    # 打印结果
    print(f"For column {col}: y at x=0 is {y_at_zero}")
    
    # 将结果添加到列表中
    y_at_zero_list.append(y_at_zero)

      # 将结果添加到字典中
    results['Column'].append(col)
    results['Y_at_X=0'].append(y_at_zero)

# 创建结果的DataFrame
results_df = pd.DataFrame(results)

# 生成输出文件名
base_filename = os.path.basename(file_paths)
name, ext = os.path.splitext(base_filename)
output_filename = f'{name}_fitted_results.csv'


# 保存结果到CSV文件
results_df.to_csv(output_filename, index=False)

# 使用第一行和计算出的y值作图
plt.figure(figsize=(8, 5))
plt.plot(data.columns[1:], y_at_zero_list, marker='o', linestyle='-', color='b', label='Y at X=0')
plt.xlabel('Columns')
plt.ylabel('Y at X=0')
plt.title('Y at X=0 for each Column')
plt.legend()
plt.xticks(np.arange(0, len(data.columns[1:]), step=50), rotation=45, ha='right')   #刻度间隔50
# plt.xticks(rotation=45)  # 旋转x轴标签以便更好显示

plt.tight_layout()  # 调整图像布局以适应标签
plt.show()

# 进行最小二乘法拟合
# degree = 2  # 拟合多项式的阶数
# coefficients = np.polyfit(x, y, 2)

# 使用拟合系数创建拟合曲线函数
# fitted_curve = np.poly1d(coefficients)

# # 绘制数据和拟合曲线
# plt.figure(figsize=(8, 5))
# plt.scatter(x, y, label='Data')
# plt.plot(x, fitted_curve(x), label='Fitted curve', color='red')
# plt.legend(loc='best')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('Data Fitting Example using Least Squares Method')
# plt.show()

# # 打印拟合系数
# print("Fitted coefficients:", coefficients)

# # 计算x无限接近于0时y的值
# y_at_zero = fitted_curve(0)

# print("y as x approaches 0:", y_at_zero)