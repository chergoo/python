from PIL import Image

im = Image.open("LISST.gif")
frames = []

try:
    while True:
        frames.append(im.copy())
        im.seek(im.tell() + 1)
except EOFError:
    pass

# 构造乒乓序列（避免首尾重复帧）
pingpong = frames + frames[-2:0:-1]

pingpong[0].save(
    "LISST_PP.gif",
    save_all=True,
    append_images=pingpong[1:],
    duration=im.info.get("duration", 100),
    loop=0
)
print("乒乓循环 GIF 已保存")