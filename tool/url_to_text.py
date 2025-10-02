from concurrent.futures import ThreadPoolExecutor, as_completed
from tool.file_to_url import pdf_to_url, ppt_to_url,excel_to_url,word_to_url
from API.vision_doubao import pdf_read
from API.text_doubao import llm
import prompt.prompt as pr
import asyncio,re


async def url_to_text(file_path,file_type,max_work=10):

    # 判断文件类型
    if file_type == "pdf":
        image_results, page_count = pdf_to_url(file_path, max_work)
        print("已经处理完PDF文件！")
    elif file_type == "pptx":
        image_results,page_count = ppt_to_url(file_path,max_work)
        print("已经处理完PPT文件！")
    elif file_type == "xlsx":
        image_results,page_count = excel_to_url(file_path,max_work)
        print("已经处理完EXCEL文件！")
    elif file_type == "docx" or file_type == "doc":
        image_results,page_count = word_to_url(file_path,max_work)
        print("已经处理完WORD文件!")
    else:
        return "文件格式不支持！"

    # 2. 并行调用大模型读取文字
    pdf_texts = [None] * len(image_results)
    completed_count = 0  # 已完成计数
    with ThreadPoolExecutor(max_workers=max_work) as executor:
        futures = {executor.submit(pdf_read, url): i for i, url in enumerate(image_results)}
        production_task = None  # 保存分类任务

        for future in as_completed(futures):
            i = futures[future]
            pdf_texts[i] = future.result()

            # 更新进度
            completed_count += 1
            print(f"进度: {completed_count}/{page_count} 页完成")

            # 确保前五页都完成了再启动分类（只启动一次）
            count = min(5, page_count)
            if production_task is None and all(pdf_texts[:count]):
                production_content = "".join(pdf_texts[:count])
                production_task = asyncio.create_task(
                    asyncio.to_thread(llm, production_content, pr.prompt_production)
                )
                print("开始并行解析产品品类...")

    # 处理产品品类判断的结果
    product_result = await production_task
    match = re.search(r"\b(00[0-8])\b", product_result)
    if match:
        product_result = match.group(1).strip()
    else:
        print(f"未匹配到产品品类，使用默认值005")
        product_result = "005"
    print(f"产品的品类：{product_result}")

    # 拼接完整的brief文件内容
    content = "".join(pdf_texts[:page_count])
    content= "最终输出 **必须为 JSON 格式**，且不能修改键值"+content+"最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！"
    print("已经成功读取全部内容！")
    to_text_result=[content,product_result,page_count]

    return to_text_result
