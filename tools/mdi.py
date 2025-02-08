from vpython import sphere, cylinder, vector, scene

def draw_3d_body(category):
    # 根据体型类别设置身体参数
    if category == "偏瘦":
        body_width = 0.5
        body_height = 1.8
        head_radius = 0.4
    elif category == "正常":
        body_width = 0.7
        body_height = 1.8
        head_radius = 0.5
    elif category == "超重":
        body_width = 1.0
        body_height = 1.7
        head_radius = 0.6
    else:
        body_width = 1.3
        body_height = 1.6
        head_radius = 0.7
    
    # 身体
    cylinder(pos=vector(0, 0, 0), axis=vector(0, body_height, 0), radius=body_width, color=vector(0.5, 0.8, 1))
    # 头部
    sphere(pos=vector(0, body_height + head_radius, 0), radius=head_radius, color=vector(1, 0.8, 0.6))
    # 左臂
    cylinder(pos=vector(-body_width, body_height * 0.7, 0), axis=vector(-0.5, -0.5, 0), radius=0.2, color=vector(1, 0.8, 0.6))
    # 右臂
    cylinder(pos=vector(body_width, body_height * 0.7, 0), axis=vector(0.5, -0.5, 0), radius=0.2, color=vector(1, 0.8, 0.6))
    # 左腿
    cylinder(pos=vector(-body_width * 0.5, 0, 0), axis=vector(-0.2, -1, 0), radius=0.3, color=vector(0.5, 0.8, 1))
    # 右腿
    cylinder(pos=vector(body_width * 0.5, 0, 0), axis=vector(0.2, -1, 0), radius=0.3, color=vector(0.5, 0.8, 1))

# 调用函数绘制不同体型的模型
draw_3d_body("超重")  # 可修改为 "偏瘦"、"正常" 或其他

# 等待用户点击后再退出
scene.waitfor('click')