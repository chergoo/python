import math
from fractions import Fraction
import tkinter as tk
from tkinter import messagebox
# x名女性，y名男性，排成一排，求男性身边有女性的概率


def get_inputs():
    def submit():
        param1 = entry1.get()
        param2 = entry2.get()
        root.result = (param1, param2)
        root.destroy()

    root = tk.Tk()
    root.title("输入参数")

    tk.Label(root, text="女性").grid(row=0, column=0)
    entry1 = tk.Entry(root)
    entry1.grid(row=0, column=1)
    tk.Label(root, text="名").grid(row=0, column=2)

    tk.Label(root, text="男性").grid(row=1, column=0)
    entry2 = tk.Entry(root)
    entry2.grid(row=1, column=1)
    tk.Label(root, text="名").grid(row=1, column=2)

    tk.Label(root, text="排成一排，求男性身边有女性的概率").grid(row=2, column=1)

    tk.Button(root, text="确认", command=submit).grid(row=3, column=0, columnspan=2)

    root.result = None
    root.mainloop()
    
    return root.result

# 计算组合数Cn
def combination(n, m):
    return math.factorial(n) / (math.factorial(m) * math.factorial(n - m))
# 计算排列数Pn
def permutation(n, m):
    return math.factorial(n) / math.factorial(n - m)

if __name__ == "__main__":
    x,y = get_inputs()
    x = int(x)
    y = int(y)
    print("女性人数：", x, "男性人数：", y)
    a = permutation(x,x) #女生排列数为P(x,x)  
    print ("女生排列数为：", a)
    b = y//2

    b1 = permutation(x+1, y)  #男性不相邻的组合数为P(x+1,y)
    print ("男生排列数为1：", b1)
    bb = b1
    for i in range(1, b+1):
        
        b_ = permutation(y, 2*i) * combination(x-1, i) * permutation(x, y-i*2)
        print (f"{i}对，男生排列数为{b_}")
        bb += b_
    
    # b2 = permutation(y,2) * combination(x-1,1) * permutation(x, y-2) #一对男性相邻的组合数
    # print ("男生排列数为2：", b2)
    # b3 = permutation(y,4) * combination(x-1,2) * permutation(x,y-4)#两对男性相邻的组合数
    # print ("男生排列数为3：", b3)
    c = permutation(x+y, x+y) #总排列数为P(10,10)
    print ("总排列数为：", c)
    # 计算概率
    # probability = a * (b1+b2+b3 )/ c
    probability = a * bb/ c
    # 将概率转换为分数形式  
    s = Fraction(probability).limit_denominator(1000)  # 分数化
    print("概率为：", s,"即",probability)  # 输出概率

    tk.messagebox.showinfo("概率结果", f"概率为：{s}，即{probability:.4f}")  # 显示概率结果
