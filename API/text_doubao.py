from openai import OpenAI
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime import AsyncArk

client = AsyncArk(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="15e0122b-bf1e-415f-873b-1cb6b39bb612"
)

client_together = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="15e0122b-bf1e-415f-873b-1cb6b39bb612"
)

model="doubao-seed-1-6-flash-250828"

json_output=[
    {
        "type": "function",
        "function": {
            "name": "generate_product_brief",
            "description": "根据输入的产品信息生成标准化的产品分析结构。",
            "strict": True,  # 强制模型遵守 JSON Schema
            "parameters": {
                "type": "object",
                "properties": {
                    "产品基础信息": {
                        "type": "object",
                        "properties": {
                            "产品品类": {"type": "string"},
                            "目标人群": {"type": "string"},
                            "使用场景": {"type": "string"},
                            "切入方向": {"type": "string"}
                        },
                        "required": ["产品品类", "目标人群", "使用场景", "切入方向"]
                    },
                    "卖点信息": {
                        "type": "object",
                        "properties": {
                            "产品主要卖点": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "产品次要卖点": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "专利背书": {"type": "string"},
                            "必带Tag": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": [
                            "产品主要卖点",
                            "产品次要卖点",
                            "专利背书",
                            "必带Tag"
                        ]
                    },
                    "创作方向": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "创作注意事项": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "产品基础信息",
                    "卖点信息",
                    "创作方向",
                    "创作注意事项"
                ]
            }
        }
    }
    ]

async def llm_json(content,prompt):

    messages=[
        {"role":"system","content":prompt},
        {"role":"user","content": content},]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        # tools = json_output,
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
        temperature=0.3
    )

    return response.choices[0].message.content