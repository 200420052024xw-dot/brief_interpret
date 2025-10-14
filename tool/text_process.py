from API.text_doubao import llm_json_again,llm,llm_json
import  prompt.prompt as pr
import json
import re

async def safe_json_loads(data: str, retry_prompt, label: str):
    """安全解析JSON并在失败时重试"""
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

def data_cleaning(content,clean_rule,default_value):
    match = re.search(clean_rule, content)
    if match:
        clean_result = match.group(1).strip()
    else:
        print(f"未匹配相关信息，使用默认值{default_value}")
        clean_result = default_value
    return clean_result


async def create_collate(content:str):
    """
    内容创作brief分模块解析：
        -> 产品基本信息
        -> 产品卖点信息
        -> 创作方向
        -> 创作要求
    """
    file_collate_selection, file_collate_create, file_collate_elegance, file_collate_type = await asyncio.gather(
        llm_json(content, pr.prompt_selection),
        llm_json(content, pr.prompt_create),
        llm(content, pr.prompt_elegance),
        llm(content[:1000], pr.prompt_production)
    )

    print("hello!")

async def selection_collate():

    print("hello!")