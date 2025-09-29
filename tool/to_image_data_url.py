from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import base64
import fitz
import os

# 将图片文件转为 data URL
def image_to_data_url(image_path: str, mime_type: str = "image/png") -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

# 将单页 PDF 转为图片并返回 data URL
def pdf_to_image(pdf_path, page_number, output_dir="images", dpi=100, quality=75):
    pdf = fitz.open(pdf_path)
    page = pdf[page_number]
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    image_path = os.path.join(output_dir, f"page_{page_number+1}.jpg")

    # 用 Pillow 保存为 JPEG
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    img = img.convert("RGB")  # 确保是 JPEG 可用模式
    img.save(image_path, format="JPEG", quality=quality, optimize=True)

    print(f"已经成功转化图片: 第 {page_number + 1} 页")

    image_url = image_to_data_url(image_path, mime_type="image/jpeg")
    print(f"已经成功转化为 url: 第 {page_number + 1} 页")

    return image_url

# 并行处理 PDF 每页，返回按页码顺序的 data URL 列表
def to_image_url(pdf_path, max_work=10, dpi=100):

    # 创建图片保存目录
    os.makedirs("images", exist_ok=True)

    # 获取 PDF 页数
    pdf = fitz.open(pdf_path)
    page_count = pdf.page_count
    print(f"PDF共有: {page_count} 页")

    # 并行处理每页
    images_url = [None] * page_count
    with ThreadPoolExecutor(max_workers=max_work) as executor:
        futures = [executor.submit(pdf_to_image, pdf_path, i, "images", dpi) for i in range(page_count)]
        for i, future in enumerate(futures):
            images_url[i] = future.result()

    return images_url, page_count
