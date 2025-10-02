from __future__ import print_function
import time
# import cloudmersive_convert_api_client
# from cloudmersive_convert_api_client.rest import ApiException
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
import aspose.slides as slides
from docx2pdf import convert
from PIL import Image
import pandas as pd
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

# def excel_to_url(excel_path,max_work):
#     # Configure API key authorization: Apikey
#     configuration = cloudmersive_convert_api_client.Configuration()
#     configuration.api_key['Apikey'] = 'YOUR_API_KEY'
#     # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
#     # configuration.api_key_prefix['Apikey'] = 'Bearer'
#
#     # create an instance of the API class
#     api_instance = cloudmersive_convert_api_client.ConvertDocumentApi(
#         cloudmersive_convert_api_client.ApiClient(configuration))
#     input_file = '/path/to/file.txt'  # file | Input file to perform the operation on.
#
#     try:
#         # Convert Document to PDF
#         api_response = api_instance.convert_document_autodetect_to_pdf(input_file)
#         pprint(api_response)
#     except ApiException as e:
#         print("Exception when calling ConvertDocumentApi->convert_document_autodetect_to_pdf: %s\n" % e)

def excel_to_url(excel_path,max_work):

    excel_file = pd.ExcelFile(excel_path)
    sheet_name = excel_file.sheet_names

    output_dir = "./Images"
    os.makedirs(output_dir, exist_ok=True)

    page_count=0
    images_url=[]

    try:
        print("截图中，请等待...")
        for sheet in sheet_name:
            safe_sheet_name = sheet.replace("/", "_").replace("\\", "_")
            image_path = f"{output_dir}/{safe_sheet_name}.png"
            excel2img.export_img(excel_path, image_path)
            images_url.append(image_to_data_url(image_path))
            page_count += 1
        print("截图完成！共处理", page_count, "个 sheet。")
    except Exception as e:
        page_count=0
        print("截图失败！", e)

    return  images_url,page_count

def word_to_url(word_path,max_work):
    #将word转化为pdf
    output_dir="./Document"
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名称
    url_hash = hashlib.md5(word_path.encode("utf-8")).hexdigest()
    filename = f"{url_hash}.pdf"
    pdf_path = os.path.join(output_dir, filename)

    # 进行转化
    convert(word_path, pdf_path)

    image_url,page_count = pdf_to_url(pdf_path,max_work)

    return image_url,page_count



