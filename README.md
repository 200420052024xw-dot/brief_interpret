# brief_interpret

一个基于 FastAPI 的 PDF 智能解读服务：
- 将 PDF 按页渲染为图片
- 使用 Doubao 视觉模型识别页面文字并保持结构
- 汇总全文并交给 Doubao 文本模型，生成“产品营销解读”结构化输出

---

## 功能特性
- **并行处理**：多线程将 PDF 页面并行转图、并行识别，显著加速。
- **结构化抽取**：输出遵循“产品信息/主要卖点/次要卖点/其他信息”的固定结构。
- **简单调用**：提供一个 POST 接口 `/pdf_collate`，输入本地 PDF 路径即可。

## 目录结构
```
brief_interpret/
  ├─ API/
  │  ├─ interpret_doubao.py     # 文本 LLM（Doubao）调用
  │  └─ vision_doubao.py        # 视觉 LLM（Doubao）调用
  ├─ tool/
  │  ├─ to_image_data_url.py    # PDF→图片（JPG）并转 Data URL
  │  ├─ to_text.py              # 并行调用视觉模型抽取文字
  │  └─ delete.py               # 清理临时图片
  ├─ images/                    # 页面图片缓存目录（运行时生成）
  ├─ main.py                    # FastAPI 入口
  └─ README.md
```

## 环境要求
- Python 3.9+（建议 3.10/3.11）
- 系统可正常安装下列依赖

建议创建虚拟环境：
```bash
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# 或 CMD
.venv\Scripts\activate.bat
```

安装依赖（示例）：
```bash
pip install fastapi uvicorn pydantic openai pillow pymupdf
```
> 说明：
> - 本项目使用 `openai` 官方 SDK 直连火山方舟（Volcengine Ark）Doubao 模型，走自定义 `base_url`。
> - `pymupdf` 对应包名为 `pymupdf`，导入名为 `fitz`。

## 模型与 API 配置
本项目默认在以下两个文件里直接使用了明文 `api_key`：
- `API/interpret_doubao.py`
- `API/vision_doubao.py`

请将其中的 `api_key="..."` 替换为你自己的火山方舟 Doubao API Key。
```startLine:endLine:API/interpret_doubao.py
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="<替换为你的 API Key>"
)
```
```startLine:endLine:API/vision_doubao.py
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="<替换为你的 API Key>"
)
```

> 更安全的做法是将 Key 放入环境变量并在代码里读取，但当前仓库并未实现环境变量读取逻辑，如需改造可自行在上述文件中读取 `os.environ["ARK_API_KEY"]`。

使用的模型（可按需替换）：
- 视觉识别：`doubao-1-5-thinking-vision-pro-250428`
- 文本解读：`doubao-seed-1-6-250615`

## 启动服务
直接运行：
```bash
python main.py
```
默认监听：`http://127.0.0.1:8000`

## 接口说明
### POST /pdf_collate
- **入参（JSON）**：
  - `pdf_path`：本地 PDF 文件路径（必填）
  - `max_work`：并行线程数（可选，默认 3；在 `tool/to_text.py` 内部默认使用到 7）
- **返回**：字符串，Doubao 文本模型基于全文提炼的“产品营销解读”。

#### 示例请求（curl）
```bash
curl -X POST "http://127.0.0.1:8000/pdf_collate" \
  -H "Content-Type: application/json" \
  -d "{\"pdf_path\": \"C:/path/to/your.pdf\", \"max_work\": 4}"
```

#### 示例请求（Python）
```python
import requests

url = "http://127.0.0.1:8000/pdf_collate"
payload = {
    "pdf_path": r"C:/path/to/your.pdf",
    "max_work": 4,
}
resp = requests.post(url, json=payload, timeout=600)
print(resp.text)
```

## 工作流程简介
1. `tool/to_image_data_url.py`：使用 `pymupdf` 将 PDF 每页渲染为 JPG，存入 `images/`，并转为 Data URL。
2. `tool/to_text.py`：并行调用视觉模型 `pdf_read()` 提取每页文本，合并成全文。
3. `API/interpret_doubao.py`：将全文交给文本模型，根据预设 Prompt 生成结构化“产品解读”。
4. `tool/delete.py`：接口返回后清理 `images/` 下的临时图片。

## 参数与性能建议
- `max_work`：并行度。CPU/内存/网速越强，可适当调大；一般 3~8 区间。
- `dpi`（在 `to_image_data_url.pdf_to_image` 中）：默认 100。更高 DPI 提升识别质量但会变慢、占用更多内存与带宽。
- `quality`（JPG 质量）：在可接受清晰度下尽量降低以加速上传。

## 常见问题（FAQ）
- 报错 `FileNotFoundError: PDF 文件不存在`：
  - 确认 `pdf_path` 为本地绝对路径，Windows 请使用 `C:/...` 或 `D:/...` 格式，或在字符串前加 `r"..."` 防止转义。
- 图片未清理或 `images/` 体积变大：
  - 接口正常返回后会调用清理；若异常中断，可手动删除 `images/` 下的 `*.jpg`。
- 模型调用超时/失败：
  - 检查网络，确认 Doubao Key 正确且有足够配额；适当降低 `max_work`。
- 识别质量不佳：
  - 提高 `dpi` 与 `quality`；确保 PDF 本身清晰。

## 安全与合规
- 当前仓库中 `API/interpret_doubao.py`、`API/vision_doubao.py` 含有明文 Key，仅用于本地演示，请务必替换为你自己的 Key，并避免提交到公共仓库。
- 输出内容应严格来源于原文件，Prompt 已限制杜撰；在重要场景中请人工复核。

## 许可证
未声明许可证（如需开源分发，请补充 LICENSE 并相应更新本文件）。
