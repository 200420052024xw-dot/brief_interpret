from tool.delete_file_image import clean_images, clean_file
from tool.url_to_file import save_file
from tool.url_to_text import url_to_text
from API.text_doubao import llm_json,llm
from pydantic import BaseModel
from fastapi import FastAPI
import prompt.prompt as pr
import asyncio
import os,json
import uvicorn

app = FastAPI()

class FileInformation(BaseModel):
    file_path: str
    max_work: int = 3

@app.post('/file_collate')
async def file_interpret(user: FileInformation):

    # 保存文件，并给出路径和文件类型
    file_path,file_type = save_file(user.file_path)

    # PDF->文本
    if file_type == "txt":
        with open(file_path,"r",encoding="utf-8") as txt:
            content=txt.read()
        product_type = llm(content,pr.prompt_production)
        print(f"产品品类：{product_type}")
    else:
        content= await url_to_text(file_path,file_type,user.max_work)
        product_type=content[1]
        content=content[0]
        if file_type=="xls":
            print(content)

    # 调用LLM 进行分析
    file_collate_selection, file_collate_create,file_collate_elegance= await asyncio.gather(
        asyncio.to_thread(llm_json, "最终输出 **必须为 JSON 格式**，且不能修改键值" + content + "最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！", pr.prompt_selection),
        asyncio.to_thread(llm_json, "最终输出 **必须为 JSON 格式**，且不能修改键值" + content + "最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！", pr.prompt_create),
        asyncio.to_thread(llm,content[0],pr.prompt_elegance)
    )

    print(f"解读选号需求：{file_collate_selection}", flush=True)
    print(f"解读创作需求：{file_collate_create}", flush=True)
    print(f"创作排版要求：{file_collate_elegance}",flush=True)

    # 转变为json格式
    file_collate_selection = json.loads(file_collate_selection)
    file_collate_create = json.loads(file_collate_create)

    # 编辑结果
    result={
        "production_type": product_type,
        "selection_requirements":file_collate_selection,
        "create_requirements":file_collate_create,
        "create_elegance":file_collate_elegance
    }

    #清除文件
    clean_images("Images")
    clean_file("./Document")

    return result

if __name__ == '__main__':
    uvicorn.run(f'{os.path.basename(__file__).split(".")[0]}:app', host='0.0.0.0', port=8845, reload=True)
