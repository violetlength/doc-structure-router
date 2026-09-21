"""模板单元测试"""
import pytest
from doc_router.templates.guide import GuideTemplate
from doc_router.templates.dictionary import DictionaryTemplate
from doc_router.templates.paper import PaperTemplate
from doc_router.templates.textbook import TextbookTemplate
from doc_router.templates.fallback import FallbackTemplate


class TestGuideTemplate:
    """测试GuideTemplate类"""

    def setup_method(self):
        self.template = GuideTemplate(chunk_size=500, chunk_overlap=100)

    def test_name(self):
        """测试模板名称"""
        assert self.template.name == "guide"

    def test_detect_positive(self, sample_guide_text):
        """测试检测指南文档 - 正面用例"""
        metadata = {"has_toc": True, "has_chapter_numbers": True}
        score = self.template.detect(sample_guide_text, metadata)
        assert score > 0

    def test_detect_negative(self, sample_dictionary_text):
        """测试检测指南文档 - 反面用例"""
        score = self.template.detect(sample_dictionary_text)
        assert score < 0.5

    def test_split_returns_list(self, sample_guide_text):
        """测试split返回列表"""
        chunks = self.template.split(sample_guide_text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_split_chunk_has_text(self, sample_guide_text):
        """测试chunk包含text"""
        chunks = self.template.split(sample_guide_text)
        non_empty = [c for c in chunks if c.text.strip()]
        assert len(non_empty) > 0

    def test_split_chunk_has_metadata(self, sample_guide_text):
        """测试chunk包含metadata"""
        chunks = self.template.split(sample_guide_text)
        for chunk in chunks:
            assert hasattr(chunk, "metadata")


class TestDictionaryTemplate:
    """测试DictionaryTemplate类"""

    def setup_method(self):
        self.template = DictionaryTemplate(chunk_size=500, chunk_overlap=100)

    def test_name(self):
        """测试模板名称"""
        assert self.template.name == "dictionary"

    def test_detect_positive(self, sample_dictionary_text):
        """测试检测词汇表文档 - 正面用例"""
        metadata = {"has_glossary": True}
        score = self.template.detect(sample_dictionary_text, metadata)
        assert score > 0

    def test_split_returns_list(self, sample_dictionary_text):
        """测试split返回列表"""
        chunks = self.template.split(sample_dictionary_text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0


class TestPaperTemplate:
    """测试PaperTemplate类"""

    def setup_method(self):
        self.template = PaperTemplate(chunk_size=500, chunk_overlap=100)

    def test_name(self):
        """测试模板名称"""
        assert self.template.name == "paper"

    def test_detect_positive(self, sample_paper_text):
        """测试检测学术论文 - 正面用例"""
        metadata = {"has_citations": True}
        score = self.template.detect(sample_paper_text, metadata)
        assert score > 0

    def test_split_returns_list(self, sample_paper_text):
        """测试split返回列表"""
        chunks = self.template.split(sample_paper_text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0


class TestTextbookTemplate:
    """测试TextbookTemplate类"""

    def setup_method(self):
        self.template = TextbookTemplate(chunk_size=500, chunk_overlap=100)

    def test_name(self):
        """测试模板名称"""
        assert self.template.name == "textbook"

    def test_detect_positive(self, sample_textbook_text):
        """测试检测教科书 - 正面用例"""
        metadata = {"has_chapter_numbers": True, "has_headings": True}
        score = self.template.detect(sample_textbook_text, metadata)
        assert score > 0

    def test_split_returns_list(self, sample_textbook_text):
        """测试split返回列表"""
        chunks = self.template.split(sample_textbook_text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0


class TestFallbackTemplate:
    """测试FallbackTemplate类"""

    def setup_method(self):
        self.template = FallbackTemplate(chunk_size=500, chunk_overlap=100)

    def test_name(self):
        """测试模板名称"""
        assert self.template.name == "fallback"

    def test_detect_always_positive(self):
        """测试fallback模板总是返回正分数"""
        text = "任意文本"
        score = self.template.detect(text)
        assert score > 0

    def test_split_returns_list(self):
        """测试split返回列表"""
        text = "这是测试内容。这是另一段内容。"
        chunks = self.template.split(text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0