import os
import re

# 目标文件夹
folder_path = os.path.join(os.getcwd(), "outputs", "plaintext")

# 遍历文件夹
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)

        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 删除中文和英文括号
        new_content = re.sub(r"[\(\)（）]", "", content)

        # 覆盖写回原文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"已处理: {filename}")

print("全部处理完成 ✅")