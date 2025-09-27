from tool.delete import clean_images, clean_file
from tool.to_text import to_content_text
import prompt.prompt as pr
from API.interpret_doubao import llm
from pydantic import BaseModel
from fastapi import FastAPI
import asyncio
import os,json
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

    with open("test_content.txt","r",encoding="utf-8") as pd:
        content=pd.read()

    # 调用 LLM
    file_collate_xuanhao, file_collate_create = await asyncio.gather(
        asyncio.to_thread(llm, "最终输出 **必须为 JSON 格式**，且不能修改键值"+content+"最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！", pr.prompt_xuanhao),
        asyncio.to_thread(llm, "最终输出 **必须为 JSON 格式**，且不能修改键值"+content+"最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！", pr.prompt_create)
    )

    print(f"解读选号需求：{file_collate_xuanhao}", flush=True)
    print(f"解读创作需求：{file_collate_create}", flush=True)

    file_collate_xuanhao = json.loads(file_collate_xuanhao)
    file_collate_create = json.loads(file_collate_create)

    # 构造 result 保持原格式

    # 清理临时文件
    clean_images("images")
    clean_file("Document")

    return {
        "selection_requirements":file_collate_xuanhao,
        "create_requirements":file_collate_create}

if __name__ == '__main__':
    uvicorn.run(f'{os.path.basename(__file__).split(".")[0]}:app', host='127.0.0.1', port=8000, reload=True)
