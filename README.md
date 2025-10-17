# Brief Interpret - 智能文档解读服务

一个基于 FastAPI 的多格式文档智能解读服务：
- 支持 PDF、Word、Excel、PPT 等多种文档格式
- 将文档转换为图片，使用豆包视觉模型识别文字内容
- 使用豆包文本模型进行结构化分析，生成产品营销解读报告
- 提供完整的选号需求、创作需求和排版要求的分析

---

## 功能特性
- **多格式支持**：支持 PDF、Word(.docx/.doc)、Excel(.xlsx)、PowerPoint(.pptx) 等格式
- **并行处理**：多线程将文档页面并行转图、并行识别，显著提升处理速度
- **智能分析**：基于豆包大模型进行产品品类识别、选号需求分析、创作需求提取
- **结构化输出**：生成标准化的 JSON 格式分析结果
- **云端兼容**：支持本地文件和 URL 链接两种输入方式

## 目录结构
```
brief_interpret/
  ├─ API/
  │  ├─ text_doubao.py         # 豆包文本模型调用
  │  └─ vision_doubao.py       # 豆包视觉模型调用
  ├─ service/
  │  ├─ file_to_url.py         # 文档转图片并生成 Data URL
  │  ├─ url_to_file.py         # 文件下载和保存
  │  ├─ url_to_text.py         # 并行调用视觉模型提取文字
  │  └─ tool.py                # 工具函数（清理文件、JSON解析等）
  ├─ log/
  │  └─ core/
  │     └─ logger.py           # 日志配置
  ├─ prompt/
  │  └─ prompt.py              # 提示词模板
  ├─ Document/                 # 临时文档存储目录
  ├─ Images/                   # 临时图片缓存目录
  ├─ main.py                   # FastAPI 服务入口
  ├─ requirements.txt          # 依赖包列表
  └─ README.md                 # 项目说明文档
```

## 环境要求
- Python 3.9+（建议 3.10/3.11）
- 操作系统：Windows、Linux、macOS
- 内存：建议 4GB 以上
- 磁盘空间：至少 1GB 可用空间

### 安装依赖

1. 创建虚拟环境（推荐）：
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

2. 安装项目依赖：
```bash
pip install -r requirements.txt
```

3. 额外系统依赖（Linux/macOS）：
```bash
# 安装 LibreOffice（用于 Excel 转换）
sudo apt-get install libreoffice  # Ubuntu/Debian
# 或
brew install libreoffice  # macOS
```

> **说明**：
> - 本项目使用 `openai` 官方 SDK 直连火山方舟（Volcengine Ark）豆包模型
> - Windows 系统支持 excel2img 进行高质量 Excel 转换
> - Linux/macOS 系统使用 LibreOffice 进行 Excel 转换

## API 配置

### 环境变量配置
项目使用 `.env` 文件管理环境变量，需要创建并配置以下内容：

1. 在项目根目录创建 `.env` 文件
2. 添加以下配置（替换为你的实际值）：

```
# 文本模型配置
TEXT_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
TEXT_API_KEY=你的火山方舟API密钥
TEXT_MODEL=doubao-seed-1-6-flash-250828

# 视觉模型配置（如需要）
VISION_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VISION_API_KEY=你的火山方舟API密钥
VISION_MODEL=doubao-seed-1-6-flash-250828
```

### 使用的模型
- **视觉识别**：`doubao-seed-1-6-flash-250828`
- **文本分析**：`doubao-seed-1-6-flash-250828`

### 安全建议
> **重要**：
> 1. 确保 `.env` 文件已添加到 `.gitignore` 中，避免将 API Key 提交到公共仓库
> 2. 生产环境中可考虑使用更安全的密钥管理方案
> 3. 定期轮换 API 密钥以提高安全性

## 启动服务

```bash
python main.py
```

服务启动后默认监听：`http://0.0.0.0:8845`

> **注意**：端口配置可以在 `main.py` 文件中修改

## API 接口

### POST /file_collate
智能文档解读接口，支持多种文档格式分析。

#### 请求参数
- `file_path`（string，必填）：文档文件路径或 URL
  - 支持本地文件路径：`C:/path/to/document.pdf`
  - 支持 HTTP/HTTPS URL：`https://example.com/document.pdf`
- `interpret_mode`（string，可选）：解读模式，默认 "我没招了"
  - `"001"`：选号模式（提取选号需求和排版要求）
  - `"002"`：创作模式（提取创作需求）
  - 其他值：全模式（提取选号需求、创作需求和排版要求）
- `max_work`（int，可选）：并行处理线程数，默认 5

#### 支持的文件格式
- PDF 文件（.pdf）
- Word 文档（.docx, .doc）
- Excel 表格（.xlsx）
- PowerPoint 演示文稿（.pptx）
- 纯文本文件（.txt）

#### 响应格式
```json
{
  "production_type": "产品品类编号（000-005）",
  "selection_requirements": {
    "产品基础信息": {...},
    "合作情况": {...},
    "目标人群/粉丝画像": {...},
    "竞品信息": {...},
    "其他要求": {...}
  },
  "create_requirements": {
    "产品基础信息": {...},
    "卖点信息": {...},
    "创作方向": [...],
    "创作注意事项": [...]
  },
  "create_elegance": "排版风格要求"
}
```

#### 示例请求

**cURL 示例**：
```bash
curl -X POST "http://127.0.0.1:8845/file_collate" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "C:/path/to/brief.pdf",
    "max_work": 5
  }'
```

**Python 示例**：
```python
import requests

url = "http://127.0.0.1:8845/file_collate"
payload = {
    "file_path": r"C:/path/to/brief.pdf",
    "max_work": 5
}

response = requests.post(url, json=payload, timeout=600)
result = response.json()
print(result)
```

## 工作流程

1. **文件处理**：`service/url_to_file.py` 处理输入文件（本地文件或 URL 下载）
2. **格式转换**：`service/file_to_url.py` 将文档转换为图片格式
   - PDF：使用 PyMuPDF 逐页渲染为图片
   - Word：转换为图片或直接读取文本
   - Excel：使用 LibreOffice 转换（Windows和Linux/macOS通用）
   - PPT：转换为PDF再转图片
3. **文字识别**：`service/url_to_text.py` 并行调用豆包视觉模型提取文字内容
4. **智能分析**：`API/text_doubao.py` 使用豆包文本模型进行结构化分析
   - 产品品类识别
   - 选号需求分析
   - 创作需求提取
   - 排版风格判断
5. **结果返回**：返回标准化的 JSON 格式分析结果
6. **清理资源**：`service/tool.py` 清理临时文件和图片

## 性能优化建议

### 参数调优
- **`max_work`**：并行线程数，建议 3-8，根据服务器性能调整
  - CPU 核心数多、内存充足：可设置 5-8
  - 内存有限：建议设置 3-5
- **`dpi`**：图片分辨率，默认 100
  - 提高 DPI 可提升识别质量，但会增加处理时间和内存占用
  - 建议范围：100-200
- **文件大小**：建议单个文件不超过 50MB

### 系统优化
- 确保有足够的磁盘空间用于临时文件存储
- 定期清理 `Document/` 和 `Images/` 目录
- 监控内存使用情况，避免内存溢出

## 常见问题

### Q: 文件处理失败
**A**: 检查以下项目：
- 文件路径是否正确（支持绝对路径和 URL）
- 文件格式是否受支持
- 文件是否损坏或加密
- 磁盘空间是否充足

### Q: API 调用超时
**A**: 可能的原因和解决方案：
- 网络连接问题：检查网络状况
- API Key 无效：确认火山方舟 API Key 正确且有足够配额
- 文件过大：减小文件大小或降低 `max_work` 参数
- 服务器性能不足：增加内存或降低并行度

### Q: 识别质量不佳
**A**: 优化建议：
- 确保原文档清晰度高
- 提高 `dpi` 参数（在 `file_to_url.py` 中）
- 检查文档是否为扫描件（扫描件识别效果更好）

### Q: 临时文件未清理
**A**: 
- 正常情况下接口返回后会自动清理
- 异常中断时可手动删除 `Document/` 和 `Images/` 目录下的文件
- 建议定期清理临时目录

## 安全注意事项

1. **API Key 安全**：
   - 生产环境请使用环境变量存储 API Key
   - 不要将包含 API Key 的代码提交到公共仓库
   - 定期轮换 API Key

2. **文件安全**：
   - 处理敏感文档时注意数据保护
   - 临时文件会自动清理，但仍需注意服务器安全
   - 建议在受信任的网络环境中运行

3. **输出内容**：
   - AI 分析结果仅供参考，重要决策请人工复核
   - 输出内容基于输入文档，请确保文档来源可靠

## 技术支持

如遇到问题，请检查：
1. Python 版本是否符合要求
2. 依赖包是否正确安装
3. API Key 配置是否正确
4. 网络连接是否正常

## 许可证

本项目仅供学习和研究使用。商业使用请遵守相关法律法规和 API 服务条款。
