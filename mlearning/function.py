import numpy
speed = [99,86,87,88,111,86,103,87,94,78,77,85,86]

l = len(speed)
print(f"列表中包含{l}个数值")

x = numpy.mean(speed)
# print("均值：",x)

y = numpy.median(speed)
# print("中值:",y)

from scipy import stats
z = stats.mode(speed)
# print("众数：",z)

var = numpy.var(speed)
# print("方差：",var) #列表中各数值与均值差的平方和。σ^2

std = numpy.std(speed)
# print("标准差:",std) #方差的平方根。σ

per = numpy.percentile(speed,75) #列表中75%的的值小于
# print("百分位数",per)

ran = numpy.random.uniform(0.00,5.99,123) #生成随机数组
# print("随机数",ran)

import matplotlib.pyplot as plt

n, bins, patches = plt.hist(ran,7) #直方图
plt.show()
# 显示每栏的数值和边界
for i in range(len(n)):
    print(f"第 {i+1} 栏: 区间 [{bins[i]:.2f}, {bins[i+1]:.2f}], 数值 {int(n[i])}")

nor = numpy.random.normal(5.0,1.0,233) #均值为5，标准差为1，数值个数233

