"""目录型模板 - 基于目录/书签结构分块"""
import re
from typing import List
from .base import BaseTemplate
from ..schemas.chunk import ChunkResult
from ..structure.models import StructureType, TOCItem


class TOCBasedTemplate(BaseTemplate):
    """目录型文档模板 - 适用于有目录/书签的文档"""

    name = "toc_based"
    description = "有目录/书签结构的教材、手册、指南等"
    detect_keywords = ["目录", "目次", "Table of Contents"]
    detect_patterns = []

    def detect(self, text: str, metadata: dict = None) -> float:
        """检测是否为目录型文档"""
        score = 0.0
        features = metadata or {}

        # 1. 检查是否有PDF书签（最可靠）
        if features.get("bookmarks"):
            return 1.0

        # 2. 检查结构类型
        if features.get("structure_type") == StructureType.TOC:
            return 0.9

        # 3. 检查文本特征
        first_text = text[:2000]

        # 检测目录关键词
        for kw in self.detect_keywords:
            if kw in first_text:
                score += 0.3
                break

        # 检测页码模式
        page_pattern = r"[.…]{2,}\d{1,4}$"
        lines = text.split("\n")[:50]
        page_matches = sum(1 for line in lines if re.search(page_pattern, line.strip()))
        if page_matches >= 3:
            score += 0.4

        return min(score, 1.0)

    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        """按目录结构分块"""
        features = metadata or {}
        
        # 获取目录结构
        toc = features.get("toc", [])
        bookmarks = features.get("bookmarks", [])
        
        # 如果没有目录，使用默认分块
        if not toc and not bookmarks:
            return self._fallback_split(text, metadata)

        # 从书签构建目录
        if bookmarks and not toc:
            toc = self._build_toc_from_bookmarks(bookmarks)

        # 按目录分块
        chunks = []
        for i, item in enumerate(toc):
            # 计算页码范围
            start_page = item.get("page", 0)
            if i + 1 < len(toc):
                end_page = toc[i + 1].get("page", start_page + 1)
            else:
                end_page = start_page + 10  # 最后一个章节，估算结束页

            # 提取该章节的文本
            content = self._extract_chapter_text(text, item, features)
            
            if content and content.strip():
                chunk_metadata = (metadata or {}).copy()
                chunk_metadata.update({
                    "chapter": item.get("title", ""),
                    "page_start": start_page,
                    "page_end": end_page,
                    "level": item.get("level", 1),
                })
                
                chunks.append(ChunkResult(
                    text=content,
                    metadata=chunk_metadata,
                ))

        return chunks if chunks else self._fallback_split(text, metadata)

    def _build_toc_from_bookmarks(self, bookmarks: list) -> list:
        """从书签构建目录"""
        toc = []
        for bm in bookmarks:
            if isinstance(bm, (list, tuple)) and len(bm) >= 3:
                toc.append({
                    "title": bm[1],
                    "level": bm[0],
                    "page": bm[2],
                })
            elif isinstance(bm, dict):
                toc.append(bm)
        return toc

    def _extract_chapter_text(self, text: str, item: dict, features: dict) -> str:
        """提取章节文本"""
        title = item.get("title", "")
        page = item.get("page", 0)
        
        # 如果有PDF页码信息，可以通过页码提取
        # 这里简化处理：按标题在文本中查找
        
        # 尝试在文本中找到标题位置
        lines = text.split("\n")
        start_idx = -1
        end_idx = len(lines)
        
        for i, line in enumerate(lines):
            if title in line and start_idx == -1:
                start_idx = i
            elif start_idx > 0 and i > start_idx:
                # 检查是否遇到同级或更高级标题
                if self._is_heading(line) and self._get_heading_level(line) <= item.get("level", 1):
                    end_idx = i
                    break
        
        if start_idx >= 0:
            content = "\n".join(lines[start_idx:end_idx])
            return content.strip()
        
        # 如果找不到标题，返回空
        return ""

    def _is_heading(self, line: str) -> bool:
        """检查是否为标题行"""
        line = line.strip()
        if not line:
            return False
        
        # Markdown标题
        if re.match(r"^#{1,6}\s+", line):
            return True
        
        # 章节编号
        if re.match(r"^第[一二三四五六七八九十百千\d]+[章节目]", line):
            return True
        
        return False

    def _get_heading_level(self, line: str) -> int:
        """获取标题层级"""
        line = line.strip()
        
        # Markdown标题
        m = re.match(r"^(#{1,6})\s+", line)
        if m:
            return len(m.group(1))
        
        # 章节编号
        if re.match(r"^第[一二三四五六七八九十百千\d]+章", line):
            return 1
        if re.match(r"^第[一二三四五六七八九十百千\d]+节", line):
            return 2
        
        return 1

    def _fallback_split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        """降级分块 - 使用段落切分"""
        paragraphs = re.split(r"\n\s*\n", text)
        
        chunks = []
        current = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current) + len(para) > self.chunk_size:
                if current:
                    chunks.append(ChunkResult(text=current))
                current = para
            else:
                current = current + "\n\n" + para if current else para
        
        if current:
            chunks.append(ChunkResult(text=current))
        
        return chunks if chunks else [ChunkResult(text=text)]
