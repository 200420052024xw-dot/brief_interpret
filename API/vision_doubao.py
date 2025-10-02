import os
from volcenginesdkarkruntime import AsyncArk

client = AsyncArk(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="15e0122b-bf1e-415f-873b-1cb6b39bb612"
)


async def pdf_read(image_url, model="doubao-seed-1-6-flash-250828"):
    """
    使用火山引擎AsyncArk接口提取图片中的文字内容

    参数:
        image_url: 图片的URL地址
        model: 批量推理接入点ID

    返回:
        提取的文字内容
    """
    try:
        # 调用火山引擎的异步聊天接口
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": """
                        请将图片中的文字内容提取出来，并保持与原始PDF中尽可能一致的逻辑结构。
                        要求：
                        1. 保留段落结构，保持自然换行。
                        2. 如果有标题，请识别并在输出中使用合适的层级标识（如“# 一级标题”，“## 二级标题”）。
                        3. 如果有公式、特殊符号，请尽量用文本表示。
                        输出内容时，只输出识别后的文字和结构，不要添加额外说明。
                        """}
                    ]
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"处理失败: {str(e)}"