from API.text_doubao import llm_json_again
import shutil
import glob
import json
import os
import re

# 删除图片
def clean_images(folder: str = "./"):
    """删除指定目录下的 png/jpg/jpeg 图片"""
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        for file in glob.glob(os.path.join(folder, ext)):
            try:
                os.remove(file)
                print(f"已删除临时图片: {file}")
            except Exception as e:
                print(f"删除失败 {file}: {e}")

# 删除临时文件
def clean_file(folder_path: str):
    """删除指定文件夹下的所有内容（文件 + 子文件夹），但保留文件夹本身"""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # 删除文件或符号链接
                print(f"已删除文件: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除文件夹及其内容
                print(f"已删除文件夹: {file_path}")
        except Exception as e:
            print(f"删除失败 {file_path}: {e}")

# 安全解析JSON并在失败时重试
async def safe_json_loads(data: str, retry_prompt, label: str):
    try:
        json_result = json.loads(data)
        print(f"{label} 转换成功")
        return json_result
    except json.JSONDecodeError:
        print(f"{label} 转换失败，正在重新尝试！")
        json_again = llm_json_again(data, retry_prompt)
        json_result = json.loads(json_again)
        print(f"{label} 转换尝试结束！")
        return json_result

# 数字提取
def data_cleaning(content,clean_rule,default_value):
    match = re.search(clean_rule, content)
    if match:
        clean_result = match.group(1).strip()
    else:
        print(f"未匹配相关信息，使用默认值{default_value}")
        clean_result = default_value
    return clean_result




