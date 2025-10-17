from volcenginesdkarkruntime import Ark
from service.file_to_url import image_to_data_url
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = Ark(
    base_url=os.getenv("VISION_BASE_URL"),
    api_key=os.getenv("VISION_API_KEY")
)

model = os.getenv("VISION_MODEL")

def image_read(image_url: str):
    completion = client.chat.completions.create(
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

if __name__ == '__main__':

    num_calls = 10
    times = []

    image_url = image_to_data_url("../Images/page_16.jpg")
    print(image_url)

    for i in range(num_calls):
        print(f"开始第 {i + 1} 次调用...")
        start = time.time()
        result= image_read(image_url)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"第 {i + 1} 次调用耗时: {elapsed:.2f} 秒")

    avg_time = sum(times) / len(times)
    print(f"\n平均响应时间: {avg_time:.2f} 秒")