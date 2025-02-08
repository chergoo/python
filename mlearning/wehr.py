import pandas as pd
import matplotlib.pyplot as plt
# from scipy.constants import h, c, k
import seaborn as sns
import numpy as np
#%matplotlib inline

# # 常数定义
# h = 6.62607015e-34  # 普朗克常数 (J·s)
# c = 3.0e8  # 光速 (m/s)
# k = 1.380649e-23  # 玻尔兹曼常数 (J/K)

# 定义普朗克定律
# def planck_lambda(wavelength, T):
#     return (2 * h * c**2) / (wavelength**5 * (np.exp((h * c) / (wavelength * k * T)) - 1))

# # 参数设置
# T = 5523.15  # 温度 (K)
# wavelengths = np.arange(100, 2500, 10) * 1e-9  # 波长范围 (100 nm 到 2500 nm)

# # 计算光谱强度
# intensity = planck_lambda(wavelengths, T)
# print(intensity)

# df = pd.read_excel("wehrli85.xlsx")
# df.info()
df = pd.read_excel("nrel.xlsx")
# print(df.head(5))?
df1 = pd.read_excel("Ed.xlsx")
df1 = pd.read_excel("230609.xlsx")
# 剔除包含 NaN 的行
df1 = df1.dropna()

# df1.info()
# df1.head(5)
x1 = df1["Wave"]
y1 = df1["Ed"]/1000


# # 滑动平均函数
# def moving_average(data, window_size):
#     window = np.ones(window_size) / window_size
#     return np.convolve(data, window, mode="valid")

# x = df["nm"]
# y = df["W/sm/nm"]
# # 计算滑动平均
# window_size = 50
# y_smooth = moving_average(y, window_size)
# x_smooth = x[:len(y_smooth)]  # 调整 x 

# #每隔两个取值
# x_sample = x [::3]# 从第 0 个开始，每隔 2 个取一个
# y_sample = y [::3]# 从第 0 个开始，每隔 2 个取一个


# fig = plt.figure(figsize = (10,6))
# 创建画布并设置背景透明
fig, ax = plt.subplots()
# fig.patch.set_facecolor('none')  # 画布背景透明
# ax.set_facecolor('none')         # 坐标区背景透明
plt.xlim(300,900)
# sns.lineplot(x = 'nm', y = 'W/sm/nm', data = df)
sns.lineplot(x="Wvlgth",y = "Etr",data=df,label = "Top of the Earth's atmosphere")
sns.lineplot(x="Wvlgth",y = "Global tilt",data=df,label = "Global tilt")
# plt.plot(wavelengths * 1e9, intensity, label=f'T = {T} K')
# sns.lineplot(x = x1,y = y1,label = "Ed")
# sns.lineplot(x = wavelengths * 1e9,y = intensity/1e13,label = "5523.15 K")
# 设置 x 轴和 y 轴标签
plt.xlabel('Wavelength/nm')
plt.ylabel('Solar spectrum/(W*m-2*nm-1)')
plt.show()

