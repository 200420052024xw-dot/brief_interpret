import shutil
import glob
import os

def clean_images(folder: str = "./"):
    """删除指定目录下的 png/jpg/jpeg 图片"""
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        for file in glob.glob(os.path.join(folder, ext)):
            try:
                os.remove(file)
                print(f"已删除临时图片: {file}")
            except Exception as e:
                print(f"删除失败 {file}: {e}")

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



