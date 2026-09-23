"""路由分发 - 主入口"""
import os
from typing import List, Optional
from ..schemas.chunk import ChunkResult, TemplateInfo
from ..core.matcher import TemplateMatcher
from ..templates.fallback import FallbackTemplate
from ..structure.detector import StructureDetector
from ..config.manager import ConfigManager


class DocumentRouter:
    """文档结构路由器 - 主入口"""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        ocr_engine: str = "paddle",
        ocr_lang: str = "ch",
        use_llm: bool = False,
    ):
        """
        Args:
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            ocr_engine: OCR引擎 (paddle/tesseract)
            ocr_lang: OCR语言
            use_llm: 是否使用LLM分析文档结构
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.ocr_engine = ocr_engine
        self.ocr_lang = ocr_lang
        self.use_llm = use_llm
        self.matcher = TemplateMatcher()
        self.structure_detector = StructureDetector()
        self._llm_analyzer = None
        self._register_builtin_templates()

    @property
    def llm_analyzer(self):
        """懒加载LLM分析器"""
        if self._llm_analyzer is None:
            from ..llm.analyzer import StructureAnalyzer
            self._llm_analyzer = StructureAnalyzer()
        return self._llm_analyzer

    def _register_builtin_templates(self):
        """注册内置模板"""
        from ..templates.guide import GuideTemplate
        from ..templates.dictionary import DictionaryTemplate
        from ..templates.textbook import TextbookTemplate
        from ..templates.paper import PaperTemplate
        from ..templates.toc_based import TOCBasedTemplate

        for cls in [TOCBasedTemplate, GuideTemplate, DictionaryTemplate, TextbookTemplate, PaperTemplate]:
            self.matcher.register(cls(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            ))

    def register(self, template):
        """注册自定义模板"""
        self.matcher.register(template)

    def analyze_structure(self, text: str, use_llm: bool = None) -> dict:
        """分析文档结构
        
        Args:
            text: 文档文本内容
            use_llm: 是否使用LLM，None则使用初始化时的设置
            
        Returns:
            结构分析结果字典
        """
        if use_llm is None:
            use_llm = self.use_llm
        
        result = {
            "structure_type": "plain",
            "confidence": 0.5,
            "description": "",
            "key_sections": [],
            "suggested_template": "fallback",
            "method": "rule_based",
        }
        
        # 规则检测
        structure = self.structure_detector.detect(text)
        result["rule_based"] = {
            "structure_type": structure.structure_type,
            "confidence": structure.confidence,
        }
        
        # LLM分析
        if use_llm:
            try:
                from ..llm.analyzer import StructureAnalyzer
                analyzer = StructureAnalyzer()
                llm_result = analyzer.analyze(text)
                
                result["llm"] = llm_result.to_dict()
                result["structure_type"] = llm_result.structure_type
                result["confidence"] = llm_result.confidence
                result["description"] = llm_result.description
                result["key_sections"] = llm_result.key_sections
                result["suggested_template"] = llm_result.suggested_template
                result["method"] = "llm"
            except Exception as e:
                result["llm_error"] = str(e)
                # 回退到规则检测
                result["structure_type"] = structure.structure_type
                result["confidence"] = structure.confidence
                result["method"] = "rule_based_fallback"
        else:
            result["structure_type"] = structure.structure_type
            result["confidence"] = structure.confidence
        
        return result

    def process(self, text: str, source: str = "", metadata: dict = None, use_llm: bool = None) -> List[ChunkResult]:
        """处理文档，返回标准化切块
        
        Args:
            text: 文档文本内容
            source: 文档来源
            metadata: 额外元数据
            use_llm: 是否使用LLM分析结构，None则使用初始化时的设置
        """
        if not text or not text.strip():
            return []

        # 合并元数据
        features = (metadata or {}).copy()
        
        # 分析文档结构
        structure_analysis = self.analyze_structure(text, use_llm=use_llm)
        features["structure_type"] = structure_analysis["structure_type"]
        features["structure_analysis"] = structure_analysis

        # 检测文档结构（规则方法）
        structure = self.structure_detector.detect(text, features)
        features["structure"] = structure

        # 获取PDF书签（如果有）
        if source and source.lower().endswith(".pdf"):
            bookmarks = self._get_pdf_bookmarks(source)
            if bookmarks:
                features["bookmarks"] = bookmarks
                features["structure_type"] = "toc"

        file_ext = os.path.splitext(source)[1].lower() if source else ""
        template = self.matcher.match(text, file_ext, features)

        if template is None:
            template = FallbackTemplate(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

        chunks = template.split(text, features)

        for i, chunk in enumerate(chunks):
            chunk.source = source
            chunk.chunk_index = i
            chunk.template_type = template.name

        return chunks

    def process_file(self, file_path: str, reader=None, pages: list = None) -> List[ChunkResult]:
        """处理文件
        
        Args:
            file_path: 文件路径
            reader: 自定义读取函数
            pages: 指定处理的页码列表（仅PDF有效），None表示处理全部
        """
        if reader is None:
            text = self._default_read(file_path, pages=pages)
        else:
            text = reader(file_path)

        return self.process(text, source=file_path)

    def _default_read(self, file_path: str, pages: list = None) -> str:
        """默认文件读取
        
        Args:
            file_path: 文件路径
            pages: 指定处理的页码列表（仅PDF有效）
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext in (".txt", ".md", ".py", ".json", ".yaml", ".yml"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        if ext == ".pdf":
            return self._read_pdf(file_path, pages=pages)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_pdf(self, file_path: str, pages: list = None) -> str:
        """PDF读取（文本提取 + OCR回退）
        
        Args:
            file_path: PDF文件路径
            pages: 指定处理的页码列表，None表示处理全部
        """
        # 1. 先尝试文本提取
        text = self._extract_text_from_pdf(file_path, pages=pages)

        # 2. 如果提取不到文本，尝试OCR
        if not text or not text.strip():
            text = self._ocr_pdf(file_path, pages=pages)

        return text or ""

    def _extract_text_from_pdf(self, file_path: str, pages: list = None) -> str:
        """从PDF提取文本（非OCR）
        
        Args:
            file_path: PDF文件路径
            pages: 指定处理的页码列表，None表示处理全部
        """
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(file_path) as pdf:
                target_pages = pages if pages is not None else range(len(pdf.pages))
                for page_idx in target_pages:
                    if 0 <= page_idx < len(pdf.pages):
                        text = pdf.pages[page_idx].extract_text()
                        if text:
                            parts.append(text)
            return "\n\n".join(parts)
        except ImportError:
            pass

        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            target_pages = pages if pages is not None else range(len(reader.pages))
            parts = []
            for page_idx in target_pages:
                if 0 <= page_idx < len(reader.pages):
                    text = reader.pages[page_idx].extract_text()
                    if text:
                        parts.append(text)
            return "\n\n".join(parts)
        except ImportError:
            pass

        return ""

    def _ocr_pdf(self, file_path: str, pages: list = None) -> str:
        """使用OCR提取PDF文本
        
        Args:
            file_path: PDF文件路径
            pages: 指定处理的页码列表，None表示处理全部
        """
        try:
            from ..ocr import get_ocr_engine
            engine = get_ocr_engine(
                engine=self.ocr_engine,
                lang=self.ocr_lang,
            )
            return engine.extract_text_from_pdf(file_path, pages=pages)
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

    def _get_pdf_bookmarks(self, file_path: str) -> list:
        """获取PDF书签"""
        try:
            import pymupdf
        except ImportError:
            try:
                import fitz as pymupdf
            except ImportError:
                return []
        
        try:
            doc = pymupdf.open(file_path)
            toc = doc.get_toc()
            doc.close()
            return toc
        except Exception:
            return []
