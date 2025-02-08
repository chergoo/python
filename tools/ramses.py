#!/usr/bin/env python3
# encoding: utf-8

# 输入处理前的数据
raw_data = [
    "23 a0 00 00 07 fe fe 03 0c 7c 0d f8 0e d3 10 ef 12 bb 15 30 19 5d 1c e6 1e e5 21 8e 25 60 29 bc 2d 55 33 ed 37 75 3a d2 3c 6e 41 9b 44 66 43 1b 41 9e 40 64 05 3f 9b 3c 9a 3e d7 41 45 45 cc 4f 76 60 b4 6d 60 76 33 80 b5",
    "23 a0 00 00 06 fe fe d2 8a 06 94 c4 9b bd a1 35 a3 58 a7 99 b1 6c bc 40 67 c4 a6 ca 7f cf e6 d0 b8 ce fd ca 7d c7 b1 c2 65 bd 64 ba b8 b9 2f ba 30 b9 32 b5 5e b2 97 b3 40 64 b5 86 b4 05 b3 8b b3 40 64 b6 2c b8 98 b7 86 b8 12",
    "23 a0 00 00 05 fe fe ac bd 1c c4 02 ca af cf d7 d3 f2 d5 6a d7 37 d9 b1 da 85 da c0 d7 36 d3 58 ce 3f c9 90 c3 68 be db b9 ce b5 b9 b1 f0 aa b3 a1 3d 9a cc 96 a3 94 58 92 75 8f 96 8c 58 89 80 86 3b 84 e8 81 4f 7f 5c",
    "23 a0 00 00 04 fe fe 25 7e f4 7d bb 7c 0e 7b 0b 79 bf 75 d5 71 40 66 6e 12 6b 0c 6a 29 6b bf 6b 53 6a a1 67 12 65 f6 62 57 60 0b 5c 7b 57 a9 54 7b 53 8c 52 ab 51 71 51 48 51 4c 4f 90 49 d3 42 ee 3e e8 3d 2a 3e e1 40 64 5d",
    # 更多数据段...
]

# 定义需要移除的模式
patterns_to_remove = ["23 a0 00 00", "fe fe", "40 64", "40 65", "40 66", "40 67"]

# 处理数据
processed_data = []
for segment in raw_data:
    # 将数据分割为字节列表
    bytes_list = segment.split()

    # 移除匹配的模式
    for pattern in patterns_to_remove:
        pattern_bytes = pattern.split()
        while True:
            try:
                # 查找模式的起始位置
                start_index = bytes_list.index(pattern_bytes[0])
                # 检查模式是否完整匹配
                if bytes_list[start_index:start_index + len(pattern_bytes)] == pattern_bytes:
                    # 删除该模式的字节
                    del bytes_list[start_index:start_index + len(pattern_bytes)]
                else:
                    break
            except ValueError:
                # 如果模式不存在，跳出循环
                break

    # 添加处理后的数据段
    processed_data.append(" ".join(bytes_list))

# 输出结果
for segment in processed_data:
    print(segment)
