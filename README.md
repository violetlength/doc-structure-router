# doc-structure-router

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-82%20passed-brightgreen.svg)]()

文档结构智能路由 - 自动检测文档结构，选择最佳切分策略

## 功能

- 自动检测文档结构（目录、章节、条目等）
- 匹配最佳切分模板（指南、字典、教材、论文等）
- 标准化输出，兼容任何向量库（ChromaDB / Milvus / PgVector）
- 支持自定义模板扩展
- **支持扫描版PDF（OCR文字识别）**

## 安装

```bash
# 基础安装（文本型PDF）
pip install -e .

# 带OCR支持（扫描版PDF）
pip install -e ".[ocr]"

# 安装所有依赖
pip install -e ".[all]"
```

### OCR依赖

插件支持两种OCR引擎：

**PaddleOCR（推荐）**：
```bash
pip install paddlepaddle paddleocr PyMuPDF
```

**Tesseract**：
```bash
pip install pytesseract Pillow PyMuPDF
# 还需要安装Tesseract程序：https://github.com/tesseract-ocr/tesseract
```

## 快速开始

```python
from doc_router import DocumentRouter

# 基础用法
router = DocumentRouter()
chunks = router.process_file("document.pdf")

for chunk in chunks:
    print(chunk.text[:100])
    print(chunk.metadata)
    print("---")
```

### 处理扫描版PDF

```python
from doc_router import DocumentRouter

# 使用PaddleOCR处理扫描版PDF
router = DocumentRouter(
    ocr_engine="paddle",  # 或 "tesseract"
    ocr_lang="ch",         # 中文
    ocr_use_gpu=False,     # 是否使用GPU
)

chunks = router.process_file("scanned_document.pdf")
print(f"切分为 {len(chunks)} 个块")
```

### 手动OCR处理

```python
from doc_router import DocumentRouter, get_ocr_engine

# 直接使用OCR引擎
ocr = get_ocr_engine("paddle", lang="ch")
text = ocr.extract_text_from_pdf("document.pdf")

# 然后用路由器处理
router = DocumentRouter()
chunks = router.process(text, source="document.pdf")
```

## 查看文档匹配信息

```python
from doc_router import DocumentRouter

router = DocumentRouter()
info = router.get_info(text)
print(info.template_type)  # e.g., "guide"
print(info.confidence)     # e.g., 0.8
```

## 内置模板

| 模板 | 适用场景 | 检测特征 |
|------|---------|---------|
| guide | 医学指南、技术手册、操作规范 | 章节编号、目录、关键词 |
| dictionary | 词汇表、术语表、药品手册 | 词汇表格式、术语解释 |
| textbook | 教科书、学习资料 | 章节结构、标题层级 |
| paper | 学术论文、研究报告 | 参考文献、摘要格式 |
| fallback | 通用兜底（段落切分） | 无特殊结构 |

## 自定义模板

```python
from doc_router import BaseTemplate, DocumentRouter
from doc_router.schemas.chunk import ChunkResult

class MyTemplate(BaseTemplate):
    name = "my_template"
    
    def detect(self, text, metadata=None):
        # 返回 0-1 的置信度
        return 0.8 if "关键词" in text else 0.0
    
    def split(self, text, metadata=None):
        # 返回 ChunkResult 列表
        return [ChunkResult(text=text)]

router = DocumentRouter()
router.register(MyTemplate())
```

## 向量库写入示例

见 `examples/` 目录：
- `chromadb_writer.py` - ChromaDB写入
- `milvus_writer.py` - Milvus写入
- `pgvector_writer.py` - PgVector写入

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行OCR测试
pytest tests/unit/test_ocr.py -v
```

## 项目结构

```
doc-structure-router/
├── doc_router/
│   ├── __init__.py          # 包入口
│   ├── core/
│   │   ├── router.py        # 主路由器
│   │   ├── matcher.py       # 模板匹配器
│   │   └── detector.py      # 文档结构检测器
│   ├── ocr/
│   │   ├── __init__.py      # OCR模块入口
│   │   └── engine.py        # OCR引擎（PaddleOCR/Tesseract）
│   ├── schemas/
│   │   └── chunk.py         # 数据结构定义
│   └── templates/
│       ├── base.py          # 模板基类
│       ├── guide.py         # 指南模板
│       ├── dictionary.py    # 词汇表模板
│       ├── textbook.py      # 教科书模板
│       ├── paper.py         # 学术论文模板
│       └── fallback.py      # 通用兜底模板
├── tests/                   # 测试用例
├── examples/                # 向量库写入示例
├── setup.py                 # 包配置
└── LICENSE                  # MIT License
```

## License

MIT
