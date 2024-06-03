#!/usr/bin/python3
#-*- coding: utf-8 -*-
 
import tkinter as tk  # 使用Tkinter前需要先导入
import random
 
# 第1步，实例化object，建立窗口window
window = tk.Tk()
 
# 第2步，给窗口的可视化起名字
window.title('My Window')
 
# 第3步，设定窗口的大小(长 * 宽)
window.geometry('500x300')  # 这里的乘是小x
 
# 第4步，在图形界面上创建一个标签label用以显示并放置
l = tk.Label(window, bg='pink', fg='white', width=20, text='empty')
l.pack()

# 创建一个Canvas小部件，用于绘制圆
canvas = tk.Canvas(window, bg='#4682B4', height=200, width=500)
canvas.pack()

# 初始圆的ID和半径
circle_id = None
initial_radius = 0


#装饰器函数
def call_counter(func):
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        print(f"Function '{func.__name__}' has been called {wrapper.calls} times.")
        #当计数大于50时清空画布并重新计数
        if wrapper.calls >=50 :
            canvas.delete("all")
            wrapper.calls = 0
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

# 第6步，定义一个触发函数功能
@call_counter#使用装饰器函数来记录函数调用次数
def print_selection(v):
    
    global circle_id
    radius =float(v)
    l.config(text='you have selected ' +v)
    # 创建随机数
    cc = random.randint(1, 500)
    kk = random.randint(1,300)
    x0, y0, x1, y1 = cc+100*radius, kk+100*radius, cc+150*radius, kk+150*radius
    oval = canvas.create_oval(x0, y0, x1, y1, fill='#A0522D')
    

# 第5步，创建一个尺度滑条，长度200字符，从0开始1结束，以0.2为刻度，精度为0.01，触发调用print_selection函数
s = tk.Scale(window, label='try me', from_=0, to=1, orient=tk.HORIZONTAL, length=200, showvalue=0,tickinterval=0.2, resolution=0.01, command=print_selection)

s.pack()


# 第7步，主窗口循环显示
window.mainloop()

