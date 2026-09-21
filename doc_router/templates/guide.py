"""指南类模板 - 医学指南、技术手册、操作规范等"""
import re
from typing import List
from .base import BaseTemplate
from ..schemas.chunk import ChunkResult


class GuideTemplate(BaseTemplate):
    """指南类文档模板"""

    name = "guide"
    description = "医学指南、技术手册、操作规范等有章节结构的文档"
    detect_keywords = ["指南", "规范", "手册", "操作", "流程", "指南", "guide", "manual"]
    detect_patterns = [
        r"第[一二三四五六七八九十\d]+章",
        r"^\d+\.\d+\s+",
    ]

    def detect(self, text: str, metadata: dict = None) -> float:
        score = 0.0
        features = metadata or {}

        if features.get("has_toc"):
            score += 0.3
        if features.get("has_chapter_numbers"):
            score += 0.3
        if features.get("has_headings"):
            score += 0.2

        first_text = text[:2000]
        for kw in self.detect_keywords:
            if kw in first_text:
                score += 0.1
                break

        return min(score, 1.0)

    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        sections = self._split_by_chapter(text)
        chunks = []
        for i, section in enumerate(sections):
            section_chunks = self._split_section(section)
            for j, chunk_text in enumerate(section_chunks):
                chunk_metadata = (metadata or {}).copy()
                chunk_metadata.update({
                    "chapter": section.get("title", ""),
                    "section_index": i,
                })
                chunks.append(ChunkResult(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    chunk_index=len(chunks),
                ))
        return chunks

    def _split_by_chapter(self, text: str) -> list:
        """按章节标题切分"""
        patterns = [
            r"^(第[一二三四五六七八九十百千\d]+章\s*.*)$",
            r"^(\d+\.\s+.*)$",
            r"^(#{1,3}\s+.*)$",
        ]

        sections = []
        current_title = ""
        current_content = []

        for line in text.split("\n"):
            matched = False
            for p in patterns:
                m = re.match(p, line.strip())
                if m:
                    if current_content:
                        sections.append({
                            "title": current_title,
                            "content": "\n".join(current_content),
                        })
                    current_title = m.group(1).strip()
                    current_content = []
                    matched = True
                    break
            if not matched:
                current_content.append(line)

        if current_content:
            sections.append({
                "title": current_title,
                "content": "\n".join(current_content),
            })

        return sections

    def _split_section(self, section: dict) -> List[str]:
        """章节内切分"""
        content = section["content"]
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
