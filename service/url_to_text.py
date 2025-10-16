import asyncio
from API.vision_doubao import image_read
from service.file_to_url import pdf_to_url, ppt_to_url, word_to_url, excel_to_url
from log.core.logger import get_logger

logger=get_logger()

async def url_to_text(file_path, file_type, max_work=10):

    # 判断文件类型,采用不同的方法转化为图片
    if file_type == "pdf":
        image_results, page_count = pdf_to_url(file_path, max_work)
        logger.info("已经处理完PDF文件！")
    elif file_type == "pptx":
        image_results, page_count = ppt_to_url(file_path, max_work)
        logger.info("已经处理完PPT文件！")
    elif file_type in ["doc", "docx"]:
        image_results, page_count = word_to_url(file_path, max_work)
        logger.info("已经处理完WORD文件！")
    elif file_type in ["xls", "xlsx"]:
        logger.info("已经处理完EXCEL！")
        image_results, page_count = excel_to_url(file_path, max_work)
    else:
        return f"文件格式不支持！{{文件类型：{file_type}}}"

    brief_content = [None] * len(image_results)
    completed_count = 0

    # 读取图片的内容
    async def image_to_text(idx, url):
        read_result = await image_read(url)
        return idx, read_result

    # 创建任务以及索引
    tasks = []
    for i, url in enumerate(image_results):
        task = asyncio.create_task(image_to_text(i, url))
        tasks.append(task)

    for image_content in asyncio.as_completed(tasks):
        idx, read_result = await image_content
        brief_content[idx] = read_result

        completed_count += 1
        logger.debug(f"进度: {completed_count}/{page_count} 页完成")

    # 拼接字符串
    content_parts = []
    for i in range(page_count):
        if brief_content[i] is not None:
            content_parts.append(f"============第{i + 1}页============\n{brief_content[i]}")
    content = "\n".join(content_parts)

    # 保存brief内容测试用
    # with open("F:\\brief_interpret-main\\test\\test_content.txt","r+",encoding="utf-8") as pd:
    #     pd.write(content)

    content = (
        "最终输出 **必须为 JSON 格式**，且不能修改键值"
        + content +
        "最终输出 **必须为 JSON 格式**，JSON 的键值需按照上述格式结构展开，不能修改键值！"
    )

    if not content or not content.strip():
        logger.error("Brief提取的文字内容为空！")

    logger.info("Brief文字提取全部完成!")

    return content
