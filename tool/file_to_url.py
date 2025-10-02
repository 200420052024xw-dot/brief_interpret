from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import aspose.slides as slides
from docx2pdf import convert
from docx import Document
from pathlib import Path
from PIL import Image
import pandas as pd
import subprocess
import excel2img
import hashlib
import base64
import fitz
import os

# 将图片文件转为 data URL
def image_to_data_url(image_path: str, mime_type: str = "image/png") -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

# 将单页 PDF 转为图片并返回 data URL
def pdf_to_image(pdf_path, page_number, output_dir="Images", dpi=100, quality=75):

    pdf = fitz.open(pdf_path)
    page = pdf[page_number]
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"page_{page_number+1}.jpg")

    # 用 Pillow 保存为 JPEG
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    img = img.convert("RGB")  # 确保是 JPEG 可用模式
    img.save(image_path, format="JPEG", quality=quality, optimize=True)
    print(f"已经成功转化图片: 第 {page_number + 1} 页")

    image_url = image_to_data_url(image_path, mime_type="image/jpeg")
    print(f"已经成功转化为 url: 第 {page_number + 1} 页")

    return image_url

# 并行处理 PDF 每页，返回按页码顺序的 data URL 列表
def pdf_to_url(pdf_path, max_work=10, dpi=100):
    os.makedirs("Images", exist_ok=True)

    # 获取 PDF 页数
    pdf = fitz.open(pdf_path)
    page_count = pdf.page_count
    print(f"PDF共有: {page_count} 页")

    # 并行处理每页
    images_url = [None] * page_count
    with ThreadPoolExecutor(max_workers=max_work) as executor:
        futures = [executor.submit(pdf_to_image, pdf_path, i, "Images", dpi) for i in range(page_count)]
        for i, future in enumerate(futures):
            images_url[i] = future.result()

    return images_url, page_count

def ppt_to_url(input_file: str, max_work: int, output_dir: str = "./Document"):

    os.makedirs(output_dir, exist_ok=True)

    # 生成完整 PDF 文件路径
    output_file = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(input_file))[0] + ".pdf"
    )

    # 用 Aspose.Slides 保存为 PDF
    with slides.Presentation(input_file) as pres:
        pres.save(output_file, slides.export.SaveFormat.PDF)
        # page_count = pres.slides.count  # 获取总页数（幻灯片数）

    # 调用你已有的 pdf_to_url 方法
    images_url, page_count = pdf_to_url(output_file, max_work)
    return images_url, page_count

def excel_to_url(excel_path, max_work=5):
    """
    Excel 转 PDF 再转图片 data URL，兼容 Linux 云端和本地。
    保留原始排版、单元格位置、图片和格式。
    """
    output_dir = "./Document"
    os.makedirs(output_dir, exist_ok=True)

    # 生成 PDF 文件路径
    pdf_filename = Path(excel_path).stem + ".pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    try:
        if os.name == "nt" and "excel2img" in globals():
            # Windows 本地可用 excel2img（保留图片和格式）
            import excel2img
            output_dir_img = "./Images"
            os.makedirs(output_dir_img, exist_ok=True)
            excel_file = pd.ExcelFile(excel_path)
            sheet_names = excel_file.sheet_names
            images_url = []
            page_count = 0
            for sheet in sheet_names:
                safe_sheet_name = sheet.replace("/", "_")
                image_path = os.path.join(output_dir_img, f"{safe_sheet_name}.png")
                excel2img.export_img(excel_path, image_path)
                images_url.append(image_to_data_url(image_path))
                page_count += 1
            return images_url, page_count
        else:
            # Linux / 云端：使用 LibreOffice 转 PDF
            subprocess.run([
                "libreoffice", "--headless", "--convert-to", "pdf",
                excel_path, "--outdir", output_dir
            ], check=True)
    except Exception as e:
        print("Excel 转 PDF 失败:", e)
        return [], 0

    # PDF → 图片 data URL
    return pdf_to_url(pdf_path, max_work)

def word_to_url(word_path, max_work=5):
    """
    将 Word 文档每页或每段文本转为图片并返回 data URL 列表
    """
    output_dir = "./Images"
    os.makedirs(output_dir, exist_ok=True)

    doc = Document(word_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    images_url = []
    page_count = 0
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux 常用字体路径
    font = ImageFont.truetype(font_path, 16)

    for i, para in enumerate(paragraphs):
        lines = para.split('\n')
        width = 800
        height = max(50, 20 * len(lines))

        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        y_text = 0
        for line in lines:
            draw.text((10, y_text), line, font=font, fill="black")
            y_text += 20

        image_path = os.path.join(output_dir, f"paragraph_{i+1}.png")
        img.save(image_path)
        images_url.append(image_to_data_url(image_path))
        page_count += 1

    return images_url, page_count


