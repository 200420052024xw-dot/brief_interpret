from tool.delete import clean_images, clean_file
from tool.to_text import to_content_text
import prompt.prompt as pr
from API.interpret_doubao import llm
from pydantic import BaseModel
from fastapi import FastAPI
import requests
import os
import hashlib
import uvicorn
import re

app = FastAPI()

class FileInformation(BaseModel):
    file_path: str
    max_work: int = 3

def extract_section(text, section_name):
    """根据标题提取段落内容"""
    pattern = rf"{section_name}[:：]\s*(.*?)(?=\n\S+:|$)"
    match = re.search(pattern, text, re.S)
    return match.group(1).strip() if match else ""

@app.post('/pdf_collate')
async def pdf_interpret(user: FileInformation):
    file_path = user.file_path

    # 确保Document文件夹存在
    file_folder = "Document"
    os.makedirs(file_folder, exist_ok=True)

    #默认数据类型为PDF
    file_type="pdf"

    # 判断是否是 URL
    if file_path.startswith("http://") or file_path.startswith("https://"):
        response = requests.get(file_path, stream=True)

        if response.status_code != 200:
            raise FileNotFoundError(f"无法下载文件: {file_path}")

        #获取文件类型
        file_type=os.path.splitext(file_path)[1].lower().split(".")[1]
        print(f"文件类型：{file_type}")

        # 使用 URL 的 MD5 生成安全文件名
        url_hash = hashlib.md5(file_path.encode("utf-8")).hexdigest()
        filename = f"{url_hash}.{file_type}"
        tmp_path = os.path.join(file_folder, filename)

        # 保存文件
        with open(tmp_path, "wb") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
        file_path = tmp_path
        print("已经成功保存文件！")

    # 本地文件不存在报错
    elif not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # PDF -> 文本
    pdf_content, page_count = to_content_text(file_path, user.max_work)

    # 调用 LLM
    file_collate_xuanhao = llm(pdf_content, pr.prompt_xuanhao)
    print(f"解读选号需求：{file_collate_xuanhao}")

    file_collate_create = llm(pdf_content, pr.prompt_create)
    print(f"解读创作需求： {file_collate_create}")

    # 宽松处理输出，将 LLM 输出当作字符串
    file_collate_create_text = file_collate_create if isinstance(file_collate_create, str) else str(file_collate_create)
    file_collate_xuanaho_text=file_collate_xuanhao if isinstance(file_collate_xuanhao,str) else str(file_collate_xuanhao)

    # 提取各段落内容
    result = {
        "选号阶段":{
            "产品基础信息":extract_section(file_collate_xuanaho_text, "产品基础信息"),
            "合作情况":extract_section(file_collate_xuanaho_text,"合作情况"),
            "其他要求":extract_section(file_collate_xuanaho_text,"其他要求"),
            "竞品信息":extract_section(file_collate_xuanaho_text,"竞品信息"),
        },
        "内容创作":{
            "产品基础信息": extract_section(file_collate_create_text, "产品基础信息"),
            "卖点信息": extract_section(file_collate_create_text, "卖点信息"),
            "创作要求": extract_section(file_collate_create_text, "创作要求"),
            "创作注意事项": extract_section(file_collate_create_text, "创作注意事项"),
            "其他信息": extract_section(file_collate_create_text, "其他信息"),
        },
    }

    # 清理临时文件
    clean_images("images")
    clean_file("Document")

    return result

if __name__ == '__main__':
    uvicorn.run(f'{os.path.basename(__file__).split(".")[0]}:app', host='127.0.0.1', port=8000, reload=True)
