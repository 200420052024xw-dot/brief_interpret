# # 前 5 页完成后启动分类
# count = min(5, page_count)
# if production_type is None and all(brief_content[:count]):
#     production_content = f"=================".join(brief_content[:count])
#     production_type = asyncio.create_task(llm(production_content, pr.prompt_production))
#     print("开始并行解析产品品类...")
#
# # 等待任务完成
# product_result = await production_type if production_type else "005"
#
# # 对产品品类进行匹配
# match = re.search(r"\b(00[0-8])\b", product_result)
# if match:
#     product_result = match.group(1).strip()
# else:
#     print(f"未匹配到产品品类，使用默认值005")
#     product_result = "005"
# print(f"产品的品类：{product_result}")

if __name__ == '__main__':
    with open("F:\\brief_interpret-main\\test\\test_content.txt","r+",encoding="utf-8") as pd:
        content = pd.read()
    print(content[:1700])
