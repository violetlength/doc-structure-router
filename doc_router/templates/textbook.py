"""教材类模板 - 教科书、学习资料等按知识点组织的文档"""
import re
from typing import List
from .base import BaseTemplate
from ..schemas.chunk import ChunkResult


class TextbookTemplate(BaseTemplate):
    """教材/教科书类文档模板"""

    name = "textbook"
    description = "教科书、学习资料等按章节+知识点组织的文档"
    detect_keywords = ["章节", "学习", "知识点", "练习", "思考题", "chapter", "lesson"]
    detect_patterns = [
        r"^第[一二三四五六七八九十百千\d]+章",
        r"^第[一二三四五六七八九十百千\d]+节",
        r"^\d+\.\d+\.\d+",
    ]

    def detect(self, text: str, metadata: dict = None) -> float:
        score = 0.0
        features = metadata or {}

        if features.get("has_toc"):
            score += 0.2
        if features.get("has_chapter_numbers"):
            score += 0.25
        if features.get("has_headings"):
            score += 0.15

        lines = text.split("\n")[:100]
        section_count = 0
        for line in lines:
            line = line.strip()
            for p in self.detect_patterns:
                if re.match(p, line):
                    section_count += 1
                    break

        if section_count >= 5:
            score += 0.2
        elif section_count >= 3:
            score += 0.1

        first_text = text[:1000]
        for kw in self.detect_keywords:
            if kw in first_text:
                score += 0.1
                break

        return min(score, 1.0)

    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        sections = self._split_by_structure(text)
        chunks = []
        for i, section in enumerate(sections):
            section_chunks = self._split_content(section["content"])
            for j, chunk_text in enumerate(section_chunks):
                chunk_metadata = (metadata or {}).copy()
                chunk_metadata.update({
                    "chapter": section.get("chapter", ""),
                    "section": section.get("section", ""),
                    "knowledge_point": section.get("title", ""),
                })
                chunks.append(ChunkResult(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    chunk_index=len(chunks),
                ))
        return chunks

    def _split_by_structure(self, text: str) -> list:
        """按章+节结构切分"""
        chapter_pattern = r"^(第[一二三四五六七八九十百千\d]+章\s*.*)$"
        section_pattern = r"^(第[一二三四五六七八九十百千\d]+节\s*.*)$"

        sections = []
        current_chapter = ""
        current_section = ""
        current_title = ""
        current_content = []

        for line in text.split("\n"):
            stripped = line.strip()

            if re.match(chapter_pattern, stripped):
                if current_content:
                    sections.append({
                        "chapter": current_chapter,
                        "section": current_section,
                        "title": current_title,
                        "content": "\n".join(current_content),
                    })
                current_chapter = stripped
                current_section = ""
                current_title = stripped
                current_content = []
            elif re.match(section_pattern, stripped):
                if current_content:
                    sections.append({
                        "chapter": current_chapter,
                        "section": current_section,
                        "title": current_title,
                        "content": "\n".join(current_content),
                    })
                current_section = stripped
                current_title = stripped
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "chapter": current_chapter,
                "section": current_section,
                "title": current_title,
                "content": "\n".join(current_content),
            })

        return sections

    def _split_content(self, content: str) -> List[str]:
        """内容内切分"""
        paragraphs = re.split(r"\n\s*\n", content)
        chunks = []
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) > self.chunk_size:
                if current:
                    chunks.append(current)
                current = para
            else:
                current = current + "\n\n" + para if current else para

        if current:
            chunks.append(current)

        return chunks if chunks else [content]
