"""文档结构检测器 - 识别文档结构类型"""
import re
from typing import Optional
from .models import StructureType, DocumentStructure, TOCItem


class StructureDetector:
    """检测文档结构类型"""

    def detect(self, text: str, metadata: dict = None) -> DocumentStructure:
        """
        检测文档结构类型
        
        Args:
            text: 文档文本
            metadata: 额外元数据（如PDF书签信息）
        
        Returns:
            DocumentStructure对象
        """
        features = metadata or {}
        
        # 1. 检查是否有PDF书签
        if features.get("bookmarks"):
            return self._build_from_bookmarks(features["bookmarks"])
        
        # 2. 检查文本中的结构特征
        scores = {
            StructureType.TOC: self._score_toc(text),
            StructureType.HEADING: self._score_heading(text),
            StructureType.CHAPTER: self._score_chapter(text),
            StructureType.GLOSSARY: self._score_glossary(text),
            StructureType.QA: self._score_qa(text),
        }
        
        # 选择得分最高的结构类型
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # 如果得分太低，返回纯文本
        if best_score < 0.3:
            return DocumentStructure(
                structure_type=StructureType.PLAIN,
                confidence=0.0,
            )
        
        # 构建结构
        if best_type == StructureType.HEADING:
            headings = self._extract_headings(text)
            return DocumentStructure(
                structure_type=best_type,
                headings=headings,
                confidence=best_score,
            )
        
        return DocumentStructure(
            structure_type=best_type,
            confidence=best_score,
        )

    def _build_from_bookmarks(self, bookmarks: list) -> DocumentStructure:
        """从PDF书签构建目录结构"""
        toc = []
        
        for bm in bookmarks:
            level, title, page = bm[0], bm[1], bm[2]
            item = TOCItem(title=title, level=level, page=page)
            toc.append(item)
        
        # 构建层级关系
        root_items = self._build_toc_hierarchy(toc)
        
        return DocumentStructure(
            structure_type=StructureType.TOC,
            toc=root_items,
            confidence=1.0,
            metadata={"source": "bookmarks"},
        )

    def _build_toc_hierarchy(self, flat_toc: list[TOCItem]) -> list[TOCItem]:
        """将扁平目录构建为层级结构"""
        root = []
        stack = []
        
        for item in flat_toc:
            # 清空栈中层级 >= 当前层级的项
            while stack and stack[-1].level >= item.level:
                stack.pop()
            
            if stack:
                stack[-1].children.append(item)
            else:
                root.append(item)
            
            stack.append(item)
        
        return root

    def _score_toc(self, text: str) -> float:
        """检测目录结构得分"""
        score = 0.0
        
        # 检测目录关键词
        toc_keywords = ["目录", "目次", "Table of Contents", "Contents"]
        first_500 = text[:500]
        for kw in toc_keywords:
            if kw in first_500:
                score += 0.3
                break
        
        # 检测页码模式 (标题....页码)
        page_pattern = r"[.…]{2,}\d{1,4}$"
        lines = text.split("\n")[:50]
        page_matches = sum(1 for line in lines if re.search(page_pattern, line.strip()))
        if page_matches >= 3:
            score += 0.4
        
        return min(score, 1.0)

    def _score_heading(self, text: str) -> float:
        """检测分级标题得分"""
        score = 0.0
        
        # 检测Markdown标题
        heading_pattern = r"^#{1,6}\s+"
        lines = text.split("\n")[:100]
        heading_count = sum(1 for line in lines if re.search(heading_pattern, line.strip()))
        
        if heading_count >= 3:
            score += 0.4
        if heading_count >= 5:
            score += 0.3
        
        # 检测多级标题
        levels = set()
        for line in lines:
            m = re.match(r"^(#{1,6})\s+", line.strip())
            if m:
                levels.add(len(m.group(1)))
        
        if len(levels) >= 2:
            score += 0.3
        
        return min(score, 1.0)

    def _score_chapter(self, text: str) -> float:
        """检测章节结构得分"""
        score = 0.0
        
        patterns = [
            r"^第[一二三四五六七八九十百千\d]+章",
            r"^第[一二三四五六七八九十百千\d]+节",
            r"^\d+\.\s+\S",
            r"^\d+\.\d+\s+\S",
        ]
        
        lines = text.split("\n")[:50]
        count = sum(1 for line in lines if any(re.search(p, line.strip()) for p in patterns))
        
        if count >= 3:
            score += 0.5
        if count >= 5:
            score += 0.3
        
        return min(score, 1.0)

    def _score_glossary(self, text: str) -> float:
        """检测词汇表结构得分"""
        score = 0.0
        
        patterns = [
            r"词汇[表解]",
            r"术语[表解]",
            r"Glossary",
            r"名词解释",
        ]
        
        first_1000 = text[:1000]
        for p in patterns:
            if re.search(p, first_1000):
                score += 0.3
                break
        
        # 检测 术语：解释 模式
        term_pattern = r"^[^\s:：]{2,10}[：:]"
        lines = text.split("\n")[:30]
        term_count = sum(1 for line in lines if re.search(term_pattern, line.strip()))
        if term_count >= 5:
            score += 0.4
        
        return min(score, 1.0)

    def _score_qa(self, text: str) -> float:
        """检测问答结构得分"""
        score = 0.0
        
        patterns = [
            r"问[：:]",
            r"答[：:]",
            r"Q[：:]",
            r"A[：:]",
            r"问题\d",
        ]
        
        count = sum(1 for p in patterns if re.search(p, text[:3000]))
        if count >= 2:
            score += 0.4
        if count >= 3:
            score += 0.3
        
        return min(score, 1.0)

    def _extract_headings(self, text: str) -> list:
        """提取分级标题"""
        from .models import HeadingNode
        
        headings = []
        current_heading = None
        current_content = []
        
        for line in text.split("\n"):
            m = re.match(r"^(#{1,6})\s+(.*)", line.strip())
            if m:
                # 保存之前的标题
                if current_heading:
                    current_heading.content = "\n".join(current_content)
                    headings.append(current_heading)
                
                # 创建新标题
                level = len(m.group(1))
                title = m.group(2)
                current_heading = HeadingNode(title=title, level=level)
                current_content = []
            else:
                current_content.append(line)
        
        # 保存最后一个标题
        if current_heading:
            current_heading.content = "\n".join(current_content)
            headings.append(current_heading)
        
        return headings
