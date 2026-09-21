"""模板匹配器单元测试"""
import pytest
from doc_router.core.matcher import TemplateMatcher
from doc_router.templates.guide import GuideTemplate
from doc_router.templates.dictionary import DictionaryTemplate
from doc_router.templates.paper import PaperTemplate


class TestTemplateMatcher:
    """测试TemplateMatcher类"""

    def setup_method(self):
        self.matcher = TemplateMatcher()

    def test_register_template(self):
        """测试注册模板"""
        template = GuideTemplate()
        self.matcher.register(template)
        assert len(self.matcher.templates) == 1

    def test_match_returns_template(self):
        """测试匹配返回模板"""
        self.matcher.register(GuideTemplate())
        text = "第一章 总则\n第二章 诊断\n第三章 治疗\n第四章 护理\n第五章 康复\n本指南旨在规范医疗行为。"
        template = self.matcher.match(text)
        assert template is not None

    def test_match_returns_none_when_no_match(self):
        """测试无匹配时返回None"""
        text = "这是一个普通文档，没有明显的结构特征"
        template = self.matcher.match(text)
        assert template is None

    def test_match_with_file_ext(self):
        """测试带文件扩展名的匹配"""
        self.matcher.register(GuideTemplate())
        text = "第一章 总则\n第二章 诊断\n第三章 治疗\n第四章 护理\n第五章 康复\n本操作规范适用于所有人员。"
        template = self.matcher.match(text, file_ext=".md")
        assert template is not None

    def test_match_all_returns_list(self):
        """测试match_all返回列表"""
        self.matcher.register(GuideTemplate())
        self.matcher.register(DictionaryTemplate())
        text = "第一章 总则\n第二章 诊断"
        results = self.matcher.match_all(text)
        assert isinstance(results, list)

    def test_match_all_sorted_by_score(self):
        """测试match_all按分数排序"""
        self.matcher.register(GuideTemplate())
        self.matcher.register(DictionaryTemplate())
        text = "第一章 总则\n第二章 诊断"
        results = self.matcher.match_all(text)
        if len(results) >= 2:
            assert results[0][1] >= results[1][1]

    def test_match_with_metadata(self):
        """测试带元数据的匹配"""
        self.matcher.register(GuideTemplate())
        text = "第一章 总则\n第二章 诊断"
        metadata = {"has_toc": True, "has_chapter_numbers": True}
        template = self.matcher.match(text, metadata=metadata)
        assert template is not None