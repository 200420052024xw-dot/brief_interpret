from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="15e0122b-bf1e-415f-873b-1cb6b39bb612"
)

def pdf_read(image_path,model="doubao-seed-1-6-flash-250828"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_path
                        },
                    },
                    {"type": "text", "text": """
                    请将图片中的文字内容提取出来，并保持与原始 PDF 中尽可能一致的逻辑结构。
                    要求：
                    1. 保留段落结构，保持自然换行。
                    2. 如果有标题，请识别并在输出中使用合适的层级标识（如“# 一级标题”，“## 二级标题”）。
                    3. 如果有公式、特殊符号，请尽量用文本表示。
                    输出内容时，只输出识别后的文字和结构，不要添加额外说明。
                    """},
                ],
            }
        ],
    )
    return response.choices[0].message.content