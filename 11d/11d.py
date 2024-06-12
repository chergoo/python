import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
import seaborn as sns

# 读取Excel文件
file1 = '21023.xlsx'
file2 = '21021.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

print (df1.shape)
print(df2.shape)
# 检查两个数据框的结构是否一致
if df1.shape != df2.shape:
    raise ValueError("The shapes of the two DataFrames do not match.")

# 计算相似性（这里我们使用欧几里德距离）
distance = euclidean(df1.values.flatten(), df2.values.flatten())
similarity = 1 / (1 + distance)

print(f"Euclidean Distance: {distance}")
print(f"Eu_Similarity: {similarity}")

# 计算相似性（这里我们使用皮尔逊相关系数）
correlation, _ = pearsonr(df1.values.flatten(), df2.values.flatten())

print(f"Pearson Correlation Coefficient: {correlation}")

#计算对应的余弦相似性
# cos_similarity = 1 - cosine(df1.values.flatten(), df2.values.flatten())

# print(f"cos_Similarity: {similarity}")

# 计算每个对应列的皮尔逊相关系数
correlations = []
for col in df1.columns:
    if df1[col].std() == 0 or df2[col].std() == 0:
        # 如果某列是常数列，设置相关系数为NaN
        correlations.append(np.nan)
    else:
        corr, _ = pearsonr(df1[col], df2[col])
        correlations.append(corr)

# # 将结果转换为DataFrame
# correlation_df = pd.DataFrame(correlations, index=df1.columns, columns=["Pearson Correlation"])

# # 绘制热图
# plt.figure(figsize=(10, 6))
# sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0)
# plt.title("Pearson Correlation Coefficient Heatmap")
# plt.show()

#指定要绘制的列
column_name = '0.253-0.298'

# 检查两个数据框中是否包含该列
if column_name not in df1.columns or column_name not in df2.columns:
    raise ValueError(f"The specified column '{column_name}' is not found in one of the dataframes.")

# 提取特定列的数据
data1 = df1[column_name]
data2 = df2[column_name]

# 绘制折线图
plt.figure(figsize=(20, 6))
plt.plot(data1, label='Data1', marker='o')
plt.plot(data2, label='Data2', marker='x')

plt.title(f'Line Plot of {column_name}')
plt.xlabel('Index')
plt.ylabel(column_name)
plt.legend()
plt.grid(True)
plt.show()