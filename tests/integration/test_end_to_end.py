"""集成测试"""
import pytest
import os
from doc_router import DocumentRouter


class TestEndToEnd:
    """端到端集成测试"""

    def setup_method(self):
        self.router = DocumentRouter(chunk_size=500, chunk_overlap=100)

    def test_process_text_returns_chunks(self):
        """测试处理文本返回chunks"""
        text = "第一章 总则\n\n第一条 为了规范医疗行为。\n\n第二条 本规范适用。"
        chunks = self.router.process(text)
        assert len(chunks) > 0
        assert all(hasattr(c, "text") for c in chunks)
        assert all(hasattr(c, "metadata") for c in chunks)

    def test_process_with_metadata(self):
        """测试带元数据处理"""
        text = "第一章 总则\n第二章 诊断"
        metadata = {"has_toc": True}
        chunks = self.router.process(text, metadata=metadata)
        assert len(chunks) > 0

    def test_process_file_txt(self):
        """测试处理TXT文件"""
        test_file = "test_doc.txt"
        content = "第一章 测试\n第二章 内容"
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(content)
            chunks = self.router.process_file(test_file)
            assert len(chunks) > 0
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_process_file_with_custom_reader(self):
        """测试使用自定义reader处理文件"""
        def custom_reader(file_path):
            return "自定义读取内容"

        chunks = self.router.process_file("test.txt", reader=custom_reader)
        assert len(chunks) > 0

    def test_chunk_result_has_id(self):
        """测试chunk_result有唯一ID"""
        text = "测试文档内容"
        chunks = self.router.process(text)
        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_result_to_dict(self):
        """测试chunk转dict"""
        text = "测试文档内容"
        chunks = self.router.process(text)
        for chunk in chunks:
            d = chunk.to_dict()
            assert "text" in d
            assert "metadata" in d
            assert "id" in d

    def test_get_info(self):
        """测试获取文档匹配信息"""
        text = "第一章 总则\n第二章 诊断\n第三章 治疗\n第四章 护理\n第五章 康复"
        info = self.router.get_info(text)
        assert info.template_type != ""
        assert 0 <= info.confidence <= 1

    def test_guide_document_processing(self):
        """测试指南类文档处理"""
        text = """第一章 总则

第一条 为了规范医疗行为，保障医疗安全。

第二条 本规范适用于医疗机构及其医务人员。

第二章 诊断

第三条 医师应当询问病史，进行体格检查。

第四条 医师应当根据患者的症状和检查结果作出诊断。

第三章 治疗

第五条 医师应当根据诊断结果制定治疗方案。"""

        chunks = self.router.process(text, source="guide.md")
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.source == "guide.md"
            assert chunk.template_type != ""

    def test_dictionary_document_processing(self):
        """测试词汇表文档处理"""
        text = """词汇表

高血压：血压持续升高的疾病。

糖尿病：血糖代谢异常的疾病。

冠心病：冠状动脉粥样硬化的疾病。"""

        chunks = self.router.process(text, source="dict.txt")
        assert len(chunks) > 0

    def test_paper_document_processing(self):
        """测试学术论文处理"""
        text = """# 摘要

目的探讨高血压患者血压控制与心血管事件的关系。

## 参考文献

[1] 张三. 高血压治疗研究[J]. 中华心血管病杂志, 2023.
[2] 李四. 血压控制研究[J]. JAMA, 2022."""

        chunks = self.router.process(text, source="paper.md")
        assert len(chunks) > 0

    def test_large_document_processing(self):
        """测试大文档处理"""
        paragraphs = []
        for i in range(50):
            paragraphs.append(f"第{i+1}段：这是测试段落内容，用于测试大文档的处理能力。")
        text = "\n\n".join(paragraphs)
        chunks = self.router.process(text)
        assert len(chunks) > 1

    def test_mixed_content_processing(self):
        """测试混合内容处理"""
        text = """这是一个普通文档。

1. 第一项
2. 第二项
3. 第三项
4. 第四项
5. 第五项"""

        chunks = self.router.process(text)
        assert len(chunks) > 0

    def test_empty_document(self):
        """测试空文档处理"""
        chunks = self.router.process("")
        assert chunks == []

    def test_single_line_document(self):
        """测试单行文档"""
        chunks = self.router.process("只有一行内容的文档")
        assert len(chunks) > 0