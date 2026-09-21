"""文档结构检测器 - 分析文档的结构特征"""
import re
from typing import Optional


class DocumentDetector:
    """检测文档的结构特征"""

    def detect_features(self, text: str, file_ext: str = "") -> dict:
        """分析文档，返回结构特征"""
        features = {
            "has_toc": self._has_toc(text),
            "has_chapter_numbers": self._has_chapter_numbers(text),
            "has_headings": self._has_headings(text),
            "has_glossary": self._has_glossary(text),
            "has_citations": self._has_citations(text),
            "has_numbered_items": self._has_numbered_items(text),
            "has_qa_format": self._has_qa_format(text),
            "avg_paragraph_length": self._avg_paragraph_length(text),
            "total_length": len(text),
            "file_ext": file_ext,
            "line_count": text.count("\n"),
        }
        return features

    def _has_toc(self, text: str) -> bool:
        """检测是否有目录"""
        toc_patterns = [
            r"目\s*录",
            r"目\s*次",
            r"Table\s+of\s+Contents",
            r"Contents",
        ]
        first_500 = text[:500]
        return any(re.search(p, first_500) for p in toc_patterns)

    def _has_chapter_numbers(self, text: str) -> bool:
        """检测是否有章节编号"""
        patterns = [
            r"^第[一二三四五六七八九十百千\d]+章",
            r"^第[一二三四五六七八九十百千\d]+节",
            r"^\d+\.\s+\S",
            r"^\d+\.\d+\s+\S",
            r"^Chapter\s+\d+",
            r"^Section\s+\d+",
        ]
        lines = text.split("\n")[:50]
        count = sum(1 for line in lines if any(re.search(p, line.strip()) for p in patterns))
        return count >= 3

    def _has_headings(self, text: str) -> bool:
        """检测是否有标题结构"""
        patterns = [
            r"^#{1,6}\s+",
            r"^[A-Z][A-Za-z\s]{2,30}$",
            r"^[\u4e00-\u9fff]{2,10}$",
        ]
        lines = text.split("\n")[:100]
        count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for p in patterns:
                if re.search(p, line):
                    count += 1
                    break
        return count >= 5

    def _has_glossary(self, text: str) -> bool:
        """检测是否有词汇表/术语表结构"""
        patterns = [
            r"词汇[表解]",
            r"术语[表解]",
            r"Glossary",
            r"名词解释",
            r"缩略语",
        ]
        first_1000 = text[:1000]
        last_1000 = text[-1000:] if len(text) > 1000 else ""
        combined = first_1000 + last_1000
        return any(re.search(p, combined) for p in patterns)

    def _has_citations(self, text: str) -> bool:
        """检测是否有参考文献"""
        patterns = [
            r"参考文献",
            r"References",
            r"Bibliography",
            r"\[\d+\]\s+",
        ]
        last_2000 = text[-2000:] if len(text) > 2000 else text
        return any(re.search(p, last_2000) for p in patterns)

    def _has_numbered_items(self, text: str) -> bool:
        """检测是否有编号列表"""
        patterns = [
            r"^\d+[.、]\s+",
            r"^\（\d+\）",
            r"^\(\d+\)",
        ]
        lines = text.split("\n")[:100]
        count = sum(1 for line in lines if any(re.search(p, line.strip()) for p in patterns))
        return count >= 5

    def _has_qa_format(self, text: str) -> bool:
        """检测是否为问答格式"""
        patterns = [
            r"问[：:]",
            r"答[：:]",
            r"Q[：:]",
            r"A[：:]",
            r"问题\d",
        ]
        count = sum(1 for p in patterns if re.search(p, text[:3000]))
        return count >= 3

    def _avg_paragraph_length(self, text: str) -> float:
        """平均段落长度"""
        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        if not paragraphs:
            return 0
        return sum(len(p) for p in paragraphs) / len(paragraphs)
