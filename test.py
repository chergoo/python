# # print("Hello echo！")

# #!/usr/bin/python3
#  ----------------------------------------------------
# 计算狗的年龄--条件语句
#  ----------------------------------------------------
# age = int(input("请输入你家狗狗的年龄: "))
# print("")
# if age <= 0:
#     print("你是在逗我吧!")
# elif age == 1:
#     print("相当于 14 岁的人。")
# elif age == 2:
#     print("相当于 22 岁的人。")
# elif age > 2:
#     human = 22 + (age -2)*5
#     print("对应人类年龄: ", human)
 
# ### 退出提示
# input("点击 enter 键退出")

#  ----------------------------------------------------
# 1-100的累乘--循环语句
# #  ----------------------------------------------------
# n = 100

# sum = 1
# counter =1
# while counter < n:
#     sum = counter*sum
#     counter = counter+1

# print("1到%d的累乘为%d" %(n,sum))
# len = len(str(sum))
# print("1到%d的累乘位数为%d" %(n,len))

# x = lambda a,b,c:a+b+c
# print(x(7,6,5))
#  ----------------------------------------------------
# 求和
# #  ----------------------------------------------------
# def sum(a,b,c):
#   x = a +b +c
# #   print("{0}、{1}、{2}的和为:{3}".format(a,b,c,x))
#   print(f"{a}、{b}、{c}的和为:{x}")
  
# a= int(input("请输入a:"))
# b= int(input("请输入b:"))
# c= int(input("请输入c:"))
# sum(a,b,c)   

#  ----------------------------------------------------
# numpy
# #  ----------------------------------------------------
# import numpy as np
# a = np.array([1,2,34+6j,6,78+8j,9,100])
# print(a[np.iscomplex(a)])

# import numpy.matlib
# import numpy as np
 
# a = np.array([[1,2],[3,4]])
# b = np.array([[11,12],[13,14]])
# print(a,b)
# print("a,b点积")
# print(np.dot(a,b))
# print("/n")
# print("a,b内积")
# print(np.inner(a,b))

# import numpy

# ages = [5,31,43,48,50,41,7,11,15,39,80,82,32,2,8,6,25,36,27,61,31]

# x = numpy.percentile(ages,75)

# print(x)


# import numpy
# import matplotlib.pyplot as plt
# from scipy import stats #导入sciPy模块

# x = numpy.random.uniform(0.0,5.0,10000)#0~5的10000个随机数
# #绘制直方图
# plt.hist(x,100)
# plt.show()

# x = numpy.random.normal(5.0,1.0,10000)#平均值为5，标准差为1，的正态分布数据。
# plt.hist(x,100)
# plt.show()


# import numpy
# import matplotlib.pyplot as plt
# from scipy import stats #导入sciPy模块
# x = [5,7,8,7,2,17,2,9,4,11,12,9,6]
# y = [99,86,87,88,111,86,103,87,94,78,77,85,86]
# # x = numpy.random.normal(5.0,1.0,1000)
# # y = numpy.random.uniform(0,20,1000)

# slope, intercept, r, p, std_err = stats.linregress(x,y)#执行方法返回重要键值


# def myfunc(x): #创建函数
#     return slope * x + intercept

# mymodel = list(map(myfunc,x)) #运行函数并生成一个新的数组

# speed = myfunc(10) #预测x为10时的y值
# print(speed)

# # math = ("r=",r,"\n","y=",slope ,"* x ","+ ",intercept)
# # print ("r=",r,"\n","y=",slope ,"* x ","+ ",intercept)
# plt.scatter(x,y) #绘制散点图
# plt.plot(x,mymodel) #绘制线性回归线
# # plt.title(math)
# # plt.legend()
# plt.text(5,75,"r=%f,y=%f*x+%f"%(r,slope,intercept)) #添加文本标签
# plt.show()

# import pandas
# from sklearn import linear_model

# df = pandas.read_csv("cars.csv") #读取csv文件
# X = df[["Weight","Volume"]] #变量X命名
# y = df[["CO2"]]   #变量y命名

# regr = linear_model.LinearRegression() #创建线性回归对象
# regr.fit(X,y)

# # # 预测重量为 2300kg、排量为 1300ccm 的汽车的二氧化碳排放量：

# # predictedCO2 = regr.predict([[2300, 1300]])

# # print(predictedCO2)

# print(regr.coef_) #打印对象的系数值

#  ----------------------------------------------------
#训练与测试
# #  ----------------------------------------------------
# import numpy
# import matplotlib.pyplot as plt
# from sklearn.metrics import r2_score #R2模块
# numpy.random.seed(2)

# x = numpy.random.normal(3, 1, 100)
# y = numpy.random.normal(150, 40, 100) / x
# #80%数据用于训练
# train_x = x[:80]
# train_y = y[:80]
# #20数据用于检验
# test_x = x[80:]
# test_y = y[80:]

# #对 train_x 和 train_y 进行多项式拟合，拟合的多项式的阶数为 4。
# mymodel = numpy.poly1d(numpy.polyfit(train_x,train_y,4)) 

# r2_train = r2_score(train_y,mymodel(train_x)) #确认训练集R2
# print(f"测试集R2为{r2_train}")
# r2_test = r2_score(test_y,mymodel(test_x)) #确认测试集R2
# print(f"测试集R2为{r2_test}")

# if r2_train >= 0.7 and r2_test >= 0.7:
#     print("该模型可信")
#     print(mymodel.coef) #打印模型系数值
#     print(mymodel(5))
# else:
#     print("该模型不可信")


# #绘制多项式回归线
# myline = numpy.linspace(0, 6, 100)

# plt.scatter(train_x, train_y)
# plt.plot(myline, mymodel(myline))
# plt.show()

# import mysql.connector
# #连接到mysql服务器
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="creesql",
#     database="mysql"
# )
# #创建游标对象
# cursor = conn.cursor()
# #执行查询
# cursor.execute("SELECT * FROM your_table")
# #获取结果
# results = cursor.fetchall()
# #打印结果
# for row in results:
#     print(row)

# #关闭游标和连接
# cursor.close()
# conn.close()

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# fig, ax = plt.subplots()
# xdata, ydata = [], []
# ln, = plt.plot([], [], 'r-', animated=True)

# def init():
#     ax.set_xlim(0, 2*np.pi)
#     ax.set_ylim(-1, 1)
#     return ln,

# def update(frame):
#     xdata.append(frame)
#     ydata.append(np.sin(frame))
#     ln.set_data(xdata, ydata)
#     return ln,

# ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128),
#                     init_func=init, blit=True)
# plt.show()
# import random

# cc=random.randint(0,100)
# print(cc)

# import torch

# # 检查 GPU 是否可用
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# print('Using device:', device)
##########################################################随机画随机颜色的线
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# # 创建一个图形窗口
# fig, ax = plt.subplots()
# xdata, ydata = [], []
# ln, = plt.plot([], [],  animated=True)  # 初始化

# # 定义全局变量 i
# i = 0

# def init():
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, 1)
#     return ln,

# def update(frame):
#     global i  # 声明使用全局变量 i
#     # ax.cla()
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, 1)
#     # 生成随机数
#     xdata.append(np.random.rand())
#     ydata.append(np.random.rand())
#     # 生成随机颜色
#     color = np.random.rand(3,)
#     ln, = ax.plot(xdata, ydata, 'o-',color = color)
#     i += 1  # 递增 i
#     print(f"Update count: {i},{color}")
#     if i > 1:
#         xdata.clear()
#         ydata.clear()
#         # ax.cla()
#         i=0
#     return ln,

# ani = FuncAnimation(fig, update, frames=np.linspace(0, 1, 128),
#                     blit=False)

# plt.show()
##########################################################API访问受限

# import numpy as np
# import requests

# # 生成随机经纬度
# def generate_random_coordinates():
#     # 生成随机的经度和纬度
#     longitude = np.random.uniform(low=-180.0, high=180.0)
#     latitude = np.random.uniform(low=-90.0, high=90.0)
#     return latitude, longitude

# # 获取地名
# def get_location_name(latitude, longitude):
    
#     url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=10&addressdetails=1"
#     response = requests.get(url)
#     print("-----------",response)
#     if response.status_code == 200:
#         data = response.json()
#         print("data:",data)
#         address = {
#             'country': data.get('address', {}).get('country', 'Unknown'),
#             'state': data.get('address', {}).get('state', 'Unknown'),
#             'town': data.get('address', {}).get('town', 'Unknown')
#         }
        
#         return address
#     else:
#         return "Unknown"
# latitude, longitude = generate_random_coordinates()
# # 获取地名
# location_name = get_location_name(latitude, longitude)

# # 打印结果
# print(f"Latitude: {latitude}, Longitude: {longitude}")
# print(f"Location Name: {location_name}")
######################################################################

from geopy.geocoders import Nominatim  
from random import uniform  
import folium
# from pyecharts.charts import Map
# from pyecharts import options as opts
# from pyecharts.globals import ChartType, GeoType
import requests
import webbrowser
import json

def random_map():  
    def generate_random_location():  
        # 生成随机经纬度（这里只是示例，实际范围可能需要根据需要调整）  
        # 中国的经纬度范围大致是从东经73°33′至135°05′，纬度从3°51′N至53°33′N。
        lat = round(uniform(18.16, 53.33) ,6) # 纬度范围：-90到90  
        lon = round(uniform(73.33, 135.05),6)  # 经度范围：-180到180  
        # 高德API Key
        YOUR_AMAP_API_KEY = 'API-key'
        
        # 经纬度
        YOUR_LATITUDE = lat
        YOUR_LONGITUDE = lon
        
        # 构建请求URL
        # url = f'https://restapi.amap.com/v3/geocode/regeo?key={YOUR_AMAP_API_KEY}&location={YOUR_LATITUDE},{YOUR_LONGITUDE}'
        url = f'https://restapi.amap.com/v3/geocode/regeo?location={YOUR_LONGITUDE},{YOUR_LATITUDE}&key={YOUR_AMAP_API_KEY}&extensions=base' 
        
        # 发送请求
        response = requests.get(url)
        print("高德返回的地址",response.text)
        
        # 解析JSON响应
        data = response.json()
        # 检查状态码，确保请求成功
        if data['status'] == '1':
                # 打印详细地址
                formatted_address = data['regeocode']['formatted_address']
                print(formatted_address)
        else:
                print('请求失败，错误码：', data['infocode'])
        return formatted_address,lat,lon

    def check():
        formatted_address,lat,lon =generate_random_location()
        
        while formatted_address ==[]:
            print("地址为查询到，正在重试...")
            formatted_address=generate_random_location()
        return formatted_address,lat,lon
        
    formatted_address,lat,lon =check()
    
    # Create a map using Folium  
    map = folium.Map(location=[lat, lon], zoom_start=12)  
            
    # Add a marker for the geocoded location  
    folium.Marker([lat, lon], popup=formatted_address).add_to(map)  
            
    # Save the map to an HTML file for visualization  
    # 保存地图到 map.html 文件
    file_path = 'map.html'
    map.save(file_path)
            
    # Display the map  
 
    print("地图已经生成")
    print(f"Random Latitude: {lat}, Longitude: {lon}")  
    # 自动在默认浏览器中打开 map.html 文件
    webbrowser.open(file_path)



    

        
  
def get_location_info(lat, lon):  
    geolocator = Nominatim(user_agent="geoapiExercises")  
    try:  
        location = geolocator.reverse((lat, lon), exactly_one=True)  
        return location.raw  
    except Exception as e:  
        return f"Error: {e}"  

def decimal_degrees_to_dms(deg):#转换经纬度
    degrees = int(deg)
    minutes = int((deg - degrees) * 60)
    seconds = ((deg - degrees) * 60 - minutes) * 60
    return degrees, minutes, seconds
  
# 生成随机经纬度  
# lat, lon = generate_random_location()  
random_map()


# 转换经纬度为度分秒格式
# lat_deg, lat_min, lat_sec = decimal_degrees_to_dms(lat)
# long_deg, long_min, long_sec = decimal_degrees_to_dms(lon)
# # lat_=({long_deg},{long_min},{long_sec})
# lon_=({lat_deg}, {lat_min},{lat_sec})
# print(f"随机生成的经度: {lat_deg}° {lat_min}' {lat_sec:.3f}\"")
# print(f"随机生成的纬度: {long_deg}° {long_min}' {long_sec:.3f}\"")


 


# # # 创建地图对象
# m = Map()
 
# # 添加数据
# m.add(formatted_address, [list((lon, lat))], "china")
# # 添加地理坐标数据
# m.set_global_opts(
#         title_opts=opts.TitleOpts(title="中国地图显示经纬度标点"),
#         visualmap_opts=opts.VisualMapOpts(max_=200, is_piecewise=True),
#     )

 

# # 渲染地图到文件，也可以使用render_notebook()在Jupyter中渲染
# m.render("高德地图.html")
# # map.render_notebook()
# # 获取并打印位置信息  
# location_info = get_location_info(lat, lon)  
# print(location_info)  
  
# # 注意：location_info是一个包含多种信息的字典，例如：  
# # {'place_id': '...', 'licence': '...', 'osm_type': '...', 'osm_id': '...', 'lat': '...', 'lon': '...', ...}  
# # 其中可能包含'display_name'字段，它提供了对应的地理位置名称  
# if 'display_name' in location_info:  
#     print(f"Approximate Location: {location_info['display_name']}")