from service.tool import clean_images, clean_file
from service.url_to_file import save_file
from service.url_to_text import url_to_text
from service.tool import safe_json_loads,data_cleaning
from API.text_doubao import llm_json,llm
from log.core.logger import get_logger
from pydantic import BaseModel
from fastapi import FastAPI
import prompt.prompt as pr
import asyncio
import uvicorn
import os

app = FastAPI()

logger = get_logger()

class FileInformation(BaseModel):
    file_path: str
    interpret_mode:str = "我没招了"
    max_work : int=5

@app.post('/file_collate')
async def file_interpret(user: FileInformation):
    """
    brief解读
    interpret_mode:
        1 -> 选号模式
        2 -> 创作模式
        3 -> 全模式（选号+创作）
    """
    logger.info(f"收到文件解读请求: {user.file_path}, 模式: {user.interpret_mode}),程序开始运行......")

    file_path, file_type = save_file(user.file_path)
    logger.info(f"Brief文件类型：{file_type}")

    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as txt:
            content = txt.read()
        file_collate_type = llm(content, pr.prompt_production)
    else:
        content = await url_to_text(file_path, file_type, user.max_work)

    if file_type in ["xls", "xlsx"]:
        logger.info(f"EXCEL的解读结果:\n{content}")

    # 按照格式提取字段
    logger.info("========================开始解析Brief========================")

    file_collate_selection = file_collate_create = file_collate_elegance = file_collate_type = None

    if user.interpret_mode == "001":
        file_collate_selection, file_collate_elegance,file_collate_type = await asyncio.gather(
            llm_json(content, pr.prompt_selection),
            llm(content, pr.prompt_elegance),
            llm(content[:1000],pr.prompt_production)
        )
        # 数据清洗
        file_collate_elegance = data_cleaning(file_collate_elegance,r"\b(00[0-1])\b","001")
        file_collate_type = data_cleaning(file_collate_type,r"\b(00[0-8])\b","005")

    elif user.interpret_mode == "002":
        file_collate_create = await llm_json(content, pr.prompt_create)

    else:
        file_collate_selection, file_collate_create, file_collate_elegance , file_collate_type= await asyncio.gather(
            llm_json(content, pr.prompt_selection),
            llm_json(content, pr.prompt_create),
            llm(content, pr.prompt_elegance),
            llm(content[:1000],pr.prompt_production)
        )
        # 数据清洗
        file_collate_elegance = data_cleaning(file_collate_elegance,r"\b(00[0-1])\b","001")
        file_collate_type = data_cleaning(file_collate_type,r"\b(00[0-8])\b","005")

    logger.info(f"选号需求解读结果:{file_collate_selection}")
    logger.info(f"内容创作解读结果:{file_collate_create}")
    logger.info(f"产品品类:{file_collate_type}")
    logger.info(f"排版要求:{file_collate_elegance}")

    # 转化为json格式
    if file_collate_selection is not None:
        file_collate_selection = await safe_json_loads(file_collate_selection, pr.prompt_selection_json, "file_collate_selection")

    if file_collate_create is not None:
        file_collate_create = await safe_json_loads(file_collate_create, pr.prompt_create_json, "file_collate_create")

    # 拼接结果
    result = {
        "production_type": file_collate_type,
        "selection_requirements": file_collate_selection,
        "create_requirements": file_collate_create,
        "create_elegance": file_collate_elegance
    }

    # # 清理临时文件
    clean_images("Images")
    clean_file("./Document")

    return result



if __name__ == '__main__':
    uvicorn.run(f'{os.path.basename(__file__).split(".")[0]}:app', host='0.0.0.0', port=8845, reload=True)
