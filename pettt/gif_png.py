import os
from PIL import Image

def extract_gif_frames(gif_path, output_folder):
    # 1. 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建文件夹: {output_folder}")

    # 2. 打开 GIF
    with Image.open(gif_path) as im:
        frame_count = 0
        try:
            while True:
                # 关键：转换成 RGBA 模式以保留透明度
                frame = im.convert("RGBA")
                
                # 生成文件名，例如 001.png, 002.png
                file_name = f"frame_{frame_count:03d}.png"
                file_path = os.path.join(output_folder, file_name)
                
                # 保存
                frame.save(file_path, "PNG")
                
                frame_count += 1
                # 移动到下一帧
                im.seek(im.tell() + 1)
                
        except EOFError:
            # 读到最后一帧后会抛出此异常，表示提取结束
            print("--- 提取完成 ---")
            print(f"共提取 {frame_count} 帧，保存在: {output_folder}")

if __name__ == "__main__":
    # --- 你可以在这里修改文件名 ---
    target_gif = "pet_normal.gif"      # 你的 GIF 文件名
    output_dir = "pet_images"   # 想保存到的文件夹名
    
    if os.path.exists(target_gif):
        extract_gif_frames(target_gif, output_dir)
    else:
        print(f"错误：找不到文件 {target_gif}")