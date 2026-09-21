"""文档结构检测器单元测试"""
import pytest
from doc_router.core.detector import DocumentDetector


class TestDocumentDetector:
    """测试DocumentDetector类"""

    def setup_method(self):
        self.detector = DocumentDetector()

    def test_detect_features_returns_dict(self):
        """测试detect_features返回字典"""
        text = "这是一个测试文档"
        features = self.detector.detect_features(text)
        assert isinstance(features, dict)

    def test_detect_features_has_all_keys(self):
        """测试detect_features返回所有必要的键"""
        text = "这是一个测试文档"
        features = self.detector.detect_features(text)
        expected_keys = [
            "has_toc",
            "has_chapter_numbers",
            "has_headings",
            "has_glossary",
            "has_citations",
            "has_numbered_items",
            "has_qa_format",
            "avg_paragraph_length",
            "total_length",
            "file_ext",
            "line_count",
        ]
        for key in expected_keys:
            assert key in features

    def test_has_toc_positive(self):
        """测试检测目录 - 正面用例"""
        text = "目录\n第一章 总则\n第二章 诊断"
        assert self.detector._has_toc(text) is True

    def test_has_toc_negative(self):
        """测试检测目录 - 反面用例"""
        text = "这是一个普通的测试文档，包含一些内容"
        assert self.detector._has_toc(text) is False

    def test_has_chapter_numbers_positive(self):
        """测试检测章节编号 - 正面用例"""
        text = """第一章 总则
第二章 诊断
第三章 治疗
第四章 护理
第五章 康复"""
        assert self.detector._has_chapter_numbers(text) is True

    def test_has_chapter_numbers_negative(self):
        """测试检测章节编号 - 反面用例"""
        text = "这是一个普通文档，没有章节编号"
        assert self.detector._has_chapter_numbers(text) is False

    def test_has_headings_positive(self):
        """测试检测标题结构 - 正面用例"""
        text = """这是标题一
内容内容内容

这是标题二
内容内容内容

这是标题三
内容内容内容

这是标题四
内容内容内容

这是标题五
内容内容内容"""
        assert self.detector._has_headings(text) is True

    def test_has_headings_negative(self):
        """测试检测标题结构 - 反面用例"""
        text = "这是一个普通段落，没有明显的标题结构。"
        assert self.detector._has_headings(text) is False

    def test_has_glossary_positive(self):
        """测试检测词汇表 - 正面用例"""
        text = "词汇表\n高血压：血压持续升高\n糖尿病：血糖代谢异常"
        assert self.detector._has_glossary(text) is True

    def test_has_glossary_negative(self):
        """测试检测词汇表 - 反面用例"""
        text = "这是一个普通的测试文档，包含一些内容"
        assert self.detector._has_glossary(text) is False

    def test_has_citations_positive(self):
        """测试检测参考文献 - 正面用例"""
        text = "这是正文内容\n\n参考文献\n[1] 张三. 论文标题[J]. 期刊, 2023."
        assert self.detector._has_citations(text) is True

    def test_has_citations_negative(self):
        """测试检测参考文献 - 反面用例"""
        text = "这是一个普通文档，没有任何引用"
        assert self.detector._has_citations(text) is False

    def test_has_numbered_items_positive(self):
        """测试检测编号列表 - 正面用例"""
        text = """1. 第一项内容
2. 第二项内容
3. 第三项内容
4. 第四项内容
5. 第五项内容"""
        assert self.detector._has_numbered_items(text) is True

    def test_has_numbered_items_negative(self):
        """测试检测编号列表 - 反面用例"""
        text = "这是一个普通段落，没有编号列表"
        assert self.detector._has_numbered_items(text) is False

    def test_has_qa_format_positive(self):
        """测试检测问答格式 - 正面用例"""
        text = "问：什么是高血压？答：高血压是血压持续升高的疾病。Q：如何治疗？A：需要长期服药。问题1：什么是糖尿病？"
        assert self.detector._has_qa_format(text) is True

    def test_has_qa_format_negative(self):
        """测试检测问答格式 - 反面用例"""
        text = "这是一个普通文档，没有问答格式"
        assert self.detector._has_qa_format(text) is False

    def test_avg_paragraph_length(self):
        """测试平均段落长度计算"""
        text = "段落一\n\n段落二\n\n段落三"
        avg_len = self.detector._avg_paragraph_length(text)
        assert avg_len > 0

    def test_detect_features_with_file_ext(self):
        """测试带文件扩展名的特征检测"""
        text = "测试文档"
        features = self.detector.detect_features(text, file_ext=".pdf")
        assert features["file_ext"] == ".pdf"