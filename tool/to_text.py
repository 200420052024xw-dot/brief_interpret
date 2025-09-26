from concurrent.futures import ThreadPoolExecutor, as_completed
from tool.to_image_data_url import to_image_url
from API.vision_doubao import pdf_read


def to_content_text(pdf_path, max_work=10):
    # 1. 并行生成图片 + data URL
    image_results, page_count = to_image_url(pdf_path, max_work)
    print("已经处理完全部PDF内容！")

    # 2. 并行调用大模型读取文字
    pdf_texts = [None] * len(image_results)
    completed_count = 0  # 已完成计数

    with ThreadPoolExecutor(max_workers=max_work) as executor:
        futures = {executor.submit(pdf_read, url): i for i, url in enumerate(image_results)}
        for future in as_completed(futures):
            i = futures[future]
            pdf_texts[i] = future.result()

            # 更新进度
            completed_count += 1
            print(f"进度: {completed_count}/{page_count} 页完成")

    content = "".join(pdf_texts[:page_count])

    content= "最终输出 **必须为 JSON 格式**，且不能修改键值"+content+"最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！"

    with open("Document\\content.txt","w",encoding="utf-8") as co:
        co.write(content)
    print("已经成功将内容保存到content.txt")

    print("已经成功读取PDF全部内容！")

    return content, page_count
