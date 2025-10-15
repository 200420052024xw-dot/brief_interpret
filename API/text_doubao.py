from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime import AsyncArk
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncArk(
    base_url=os.getenv("TEXT_BASE_URL"),
    api_key=os.getenv("TEXT_API_KEY")
)

client_together = Ark(
    base_url=os.getenv("TEXT_BASE_URL"),
    api_key=os.getenv("TEXT_API_KEY")
)

model=os.getenv("TEXT_MODEL")

async def llm_json(content,prompt):
    messages=[
        {"role":"system","content":prompt},
        {"role":"user","content": content},]
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        thinking = {
            "type": "disabled"  # 不使用深度思考能力,
            # "type": "enabled" # 使用深度思考能力
            # "type": "auto" # 模型自行判断是否使用深度思考能力
        },
        temperature = 0.3
    )
    return response.choices[0].message.content


async def llm(content,prompt):
    messages=[
        {"role":"system","content":prompt},
        {"role":"user","content": content},]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        thinking = {
            "type": "disabled"  # 不使用深度思考能力,
            # "type": "enabled" # 使用深度思考能力
            # "type": "auto" # 模型自行判断是否使用深度思考能力
        },
        temperature = 0.3
    )
    return response.choices[0].message.content


def llm_json_again(content,prompt):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content}, ]
    response = client_together.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        thinking={
            "type": "disabled"  # 不使用深度思考能力,
            # "type": "enabled" # 使用深度思考能力
            # "type": "auto" # 模型自行判断是否使用深度思考能力
        },
        temperature=0.3
    )
    return response.choices[0].message.content