from prompt.prompt import prompt_create as prompt
import requests
import json

url = "https://api.rcouyi.com/v1/chat/completions"

with open("F:\\brief_interpret-main\\test\\test_content.txt","r+",encoding="utf-8") as pd:
    user_input=pd.read()

payload = json.dumps({
    "model": "gpt-4o",
    "messages":[
        {
            "role": "system",
            "content": prompt
        },
        {"role": "user", "content": user_input}
    ],
    "tools" : [
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
})
headers = {
   'Authorization': 'Bearer sk-IfXIJkC4cTJ0AfcUDb701f0fD4F941EcB6501b01F2F0F1F4',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
response_dict = response.json()  # 关键：将Response对象转JSON字典
content_str = response_dict["choices"][0]["message"]["content"]  # 提取核心内容
clean_content = content_str.strip().strip("```json").strip("```")  # 去除JSON包裹标记
final_data = json.loads(clean_content)  # 解析嵌套的JSON

# 3. 打印结果（或按需求使用final_data）
print(json.dumps(final_data, ensure_ascii=False, indent=2))
