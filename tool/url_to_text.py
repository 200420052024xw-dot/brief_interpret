import asyncio
import re
from API.vision_doubao import pdf_read
from API.text_doubao import llm
import prompt.prompt as pr
from tool.file_to_url import pdf_to_url, ppt_to_url


async def url_to_text(file_path, file_type, max_work=10):
    # 判断文件类型
    if file_type == "pdf":
        image_results, page_count = pdf_to_url(file_path, max_work)
        print("已经处理完PDF文件！")
    elif file_type == "pptx":
        image_results, page_count = ppt_to_url(file_path, max_work)
        print("已经处理完PPT文件！")
    else:
        return "文件格式不支持！"

    pdf_texts = [None] * len(image_results)
    completed_count = 0
    production_task = None

    async def wrap_task(idx, url):
        result = await pdf_read(url)
        return idx, result

    # 创建任务
    tasks = [asyncio.create_task(wrap_task(i, url)) for i, url in enumerate(image_results)]

    for fut in asyncio.as_completed(tasks):
        idx, result = await fut
        pdf_texts[idx] = result

        completed_count += 1
        print(f"进度: {completed_count}/{page_count} 页完成")

        # 前 5 页完成后启动分类
        count = min(5, page_count)
        if production_task is None and all(pdf_texts[:count]):
            production_content = "".join(pdf_texts[:count])
            production_task = asyncio.create_task(llm(production_content, pr.prompt_production))
            print("开始并行解析产品品类...")

        # 等待分类任务
        product_result = await production_task if production_task else "005"

    match = re.search(r"\b(00[0-8])\b", product_result)
    if match:
        product_result = match.group(1).strip()
    else:
        print(f"未匹配到产品品类，使用默认值005")
        product_result = "005"
    print(f"产品的品类：{product_result}")

    # 拼接完整内容
    content = "".join(pdf_texts[:page_count])
    content = (
        "最终输出 **必须为 JSON 格式**，且不能修改键值"
        + content +
        "最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！"
    )
    print("已经成功读取全部内容！")

    return [content, product_result, page_count]
