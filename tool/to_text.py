from concurrent.futures import ThreadPoolExecutor, as_completed
from tool.to_image_data_url import to_image_url
from API.vision_doubao import pdf_read
from API.interpret_doubao import llm
import prompt.prompt as pr
import asyncio


async def to_content_text(pdf_path, max_work=10):
    # 1. 并行生成图片 + data URL
    image_results, page_count = to_image_url(pdf_path, max_work)
    print("已经处理完全部PDF内容！")

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
            if production_task is None and all(pdf_texts[:5]):
                production_content = "".join(pdf_texts[:5])
                production_task = asyncio.create_task(
                    asyncio.to_thread(llm, production_content, pr.prompt_production)
                )
                print("开始并行解析产品品类...")

    product_result = await production_task

    if product_result=="000":
        product_result=""
    elif product_result=="001":
        product_result=""
    elif product_result=="002":
        product_result=""
    elif product_result=="003":
        product_result=""
    elif product_result=="004":
        product_result=""
    else:
        product_result=""

    print(f"产品的品类：{product_result}")

    content = "".join(pdf_texts[:page_count])

    content= "最终输出 **必须为 JSON 格式**，且不能修改键值"+content+"最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！"

    # with open("test\\test_content.txt","w",encoding="utf-8") as co:
    #     co.write(content)
    # print("已经成功将内容保存到test_content.txt")

    print("已经成功读取PDF全部内容！")

    return content,product_result,page_count
