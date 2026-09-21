"""路由分发 - 主入口"""
import os
from typing import List, Optional
from ..schemas.chunk import ChunkResult, TemplateInfo
from ..core.matcher import TemplateMatcher
from ..templates.fallback import FallbackTemplate


class DocumentRouter:
    """文档结构路由器 - 主入口"""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        ocr_engine: str = "paddle",
        ocr_lang: str = "ch",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.ocr_engine = ocr_engine
        self.ocr_lang = ocr_lang
        self.matcher = TemplateMatcher()
        self._register_builtin_templates()

    def _register_builtin_templates(self):
        """注册内置模板"""
        from ..templates.guide import GuideTemplate
        from ..templates.dictionary import DictionaryTemplate
        from ..templates.textbook import TextbookTemplate
        from ..templates.paper import PaperTemplate

        for cls in [GuideTemplate, DictionaryTemplate, TextbookTemplate, PaperTemplate]:
            self.matcher.register(cls(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            ))

    def register(self, template):
        """注册自定义模板"""
        self.matcher.register(template)

    def process(self, text: str, source: str = "", metadata: dict = None) -> List[ChunkResult]:
        """处理文档，返回标准化切块"""
        if not text or not text.strip():
            return []

        file_ext = os.path.splitext(source)[1].lower() if source else ""
        template = self.matcher.match(text, file_ext, metadata)

        if template is None:
            template = FallbackTemplate(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

        chunks = template.split(text, metadata)

        for i, chunk in enumerate(chunks):
            chunk.source = source
            chunk.chunk_index = i
            chunk.template_type = template.name

        return chunks

    def process_file(self, file_path: str, reader=None) -> List[ChunkResult]:
        """处理文件"""
        if reader is None:
            text = self._default_read(file_path)
        else:
            text = reader(file_path)

        return self.process(text, source=file_path)

    def _default_read(self, file_path: str) -> str:
        """默认文件读取"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext in (".txt", ".md", ".py", ".json", ".yaml", ".yml"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        if ext == ".pdf":
            return self._read_pdf(file_path)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_pdf(self, file_path: str) -> str:
        """PDF读取（文本提取 + OCR回退）"""
        # 1. 先尝试文本提取
        text = self._extract_text_from_pdf(file_path)

        # 2. 如果提取不到文本，尝试OCR
        if not text or not text.strip():
            text = self._ocr_pdf(file_path)

        return text or ""

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """从PDF提取文本（非OCR）"""
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        parts.append(text)
            return "\n\n".join(parts)
        except ImportError:
            pass

        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            parts = [page.extract_text() for page in reader.pages if page.extract_text()]
            return "\n\n".join(parts)
        except ImportError:
            pass

        return ""

    def _ocr_pdf(self, file_path: str) -> str:
        """使用OCR提取PDF文本"""
        try:
            from ..ocr import get_ocr_engine
            engine = get_ocr_engine(
                engine=self.ocr_engine,
                lang=self.ocr_lang,
            )
            return engine.extract_text_from_pdf(file_path)
        except ImportError as e:
            raise ImportError(
                f"PDF无可提取文本，需要安装OCR依赖进行文字识别。\n"
                f"错误信息: {e}\n"
                f"安装命令:\n"
                f"  pip install paddlepaddle paddleocr PyMuPDF\n"
                f"或使用自定义reader:\n"
                f"  router.process_file('doc.pdf', reader=your_ocr_reader)"
            )

    def get_info(self, text: str, source: str = "") -> TemplateInfo:
        """查看文档匹配信息（不切分）"""
        file_ext = os.path.splitext(source)[1].lower() if source else ""
        template = self.matcher.match(text, file_ext)

        if template is None:
            return TemplateInfo(
                template_type="fallback",
                confidence=0.0,
            )

        return TemplateInfo(
            template_type=template.name,
            confidence=template.detect(text),
            detect_rules_matched=template.detect_keywords,
        )
