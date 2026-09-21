"""文档路由器单元测试"""
import pytest
from doc_router import DocumentRouter


class TestDocumentRouter:
    """测试DocumentRouter类"""

    def setup_method(self):
        self.router = DocumentRouter(chunk_size=500, chunk_overlap=100)

    def test_init_default_values(self):
        """测试默认初始化值"""
        router = DocumentRouter()
        assert router.chunk_size == 800
        assert router.chunk_overlap == 150

    def test_init_custom_values(self):
        """测试自定义初始化值"""
        router = DocumentRouter(chunk_size=1000, chunk_overlap=200)
        assert router.chunk_size == 1000
        assert router.chunk_overlap == 200

    def test_process_returns_list(self, sample_guide_text):
        """测试process返回列表"""
        chunks = self.router.process(sample_guide_text)
        assert isinstance(chunks, list)

    def test_process_empty_text(self):
        """测试处理空文本"""
        chunks = self.router.process("")
        assert chunks == []

    def test_process_whitespace_text(self):
        """测试处理空白文本"""
        chunks = self.router.process("   \n\t  ")
        assert chunks == []

    def test_process_with_source(self, sample_guide_text):
        """测试带source的处理"""
        chunks = self.router.process(sample_guide_text, source="test.md")
        assert len(chunks) > 0
        assert chunks[0].source == "test.md"

    def test_process_chunk_has_metadata(self, sample_guide_text):
        """测试chunk包含metadata"""
        chunks = self.router.process(sample_guide_text)
        assert len(chunks) > 0
        assert "id" in chunks[0].metadata
        assert "doc_type" in chunks[0].metadata

    def test_process_chunk_has_template_type(self, sample_guide_text):
        """测试chunk包含template_type"""
        chunks = self.router.process(sample_guide_text)
        assert len(chunks) > 0
        assert chunks[0].template_type != ""

    def test_process_guide_text(self, sample_guide_text):
        """测试处理指南类文档"""
        chunks = self.router.process(sample_guide_text)
        assert len(chunks) > 0
        template_types = [c.template_type for c in chunks]
        assert any(t in ["guide", "textbook"] for t in template_types)

    def test_process_dictionary_text(self, sample_dictionary_text):
        """测试处理词汇表文档"""
        chunks = self.router.process(sample_dictionary_text)
        assert len(chunks) > 0

    def test_process_paper_text(self, sample_paper_text):
        """测试处理学术论文"""
        chunks = self.router.process(sample_paper_text)
        assert len(chunks) > 0

    def test_get_info_returns_template_info(self, sample_guide_text):
        """测试get_info返回TemplateInfo"""
        from doc_router.schemas.chunk import TemplateInfo
        info = self.router.get_info(sample_guide_text)
        assert isinstance(info, TemplateInfo)

    def test_get_info_has_template_type(self, sample_guide_text):
        """测试get_info包含template_type"""
        info = self.router.get_info(sample_guide_text)
        assert hasattr(info, "template_type")

    def test_get_info_has_confidence(self, sample_guide_text):
        """测试get_info包含confidence"""
        info = self.router.get_info(sample_guide_text)
        assert hasattr(info, "confidence")
        assert 0 <= info.confidence <= 1

    def test_register_custom_template(self, sample_guide_text):
        """测试注册自定义模板"""
        from doc_router.templates.base import BaseTemplate
        from doc_router.schemas.chunk import ChunkResult

        class CustomTemplate(BaseTemplate):
            name = "custom"

            def detect(self, text, metadata=None):
                return 0.5

            def split(self, text, metadata=None):
                return [ChunkResult(text=text)]

        router = DocumentRouter()
        router.register(CustomTemplate())
        assert len(router.matcher.templates) > 0