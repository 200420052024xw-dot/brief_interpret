from tool.delete import clean_images, clean_file
from tool.to_text import to_content_text
from API.interpret_doubao import llm_json
from pydantic import BaseModel
from fastapi import FastAPI
import prompt.prompt as pr
import requests
import asyncio
import os,json
import hashlib
import uvicorn

app = FastAPI()

class FileInformation(BaseModel):
    file_path: str
    max_work: int = 3

@app.post('/pdf_collate')
async def pdf_interpret(user: FileInformation):
    file_path = user.file_path

    # 确保Document文件夹存在
    file_folder = "./Document"
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
    content, product_type, page_count = await to_content_text(file_path, user.max_work)

    clean_images("images")
    clean_file("./Document")

    # 调用 LLM
    file_collate_xuanhao, file_collate_create = await asyncio.gather(
        asyncio.to_thread(llm_json, "最终输出 **必须为 JSON 格式**，且不能修改键值" + content + "最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！", pr.prompt_xuanhao),
        asyncio.to_thread(llm_json, "最终输出 **必须为 JSON 格式**，且不能修改键值" + content + "最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！", pr.prompt_create)
    )

    print(f"解读选号需求：{file_collate_xuanhao}", flush=True)
    print(f"解读创作需求：{file_collate_create}", flush=True)

    file_collate_xuanhao = json.loads(file_collate_xuanhao)
    file_collate_create = json.loads(file_collate_create)


    return {
        "selection_requirements":file_collate_xuanhao,
        "create_requirements":file_collate_create,
        "production_type":product_type
    }

if __name__ == '__main__':
    uvicorn.run(f'{os.path.basename(__file__).split(".")[0]}:app', host='0.0.0.0', port=8845, reload=True)
