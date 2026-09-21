"""论文类模板 - 学术论文、研究报告等"""
import re
from typing import List
from .base import BaseTemplate
from ..schemas.chunk import ChunkResult


class PaperTemplate(BaseTemplate):
    """学术论文/研究报告类文档模板"""

    name = "paper"
    description = "学术论文、研究报告、白皮书等"
    detect_keywords = ["摘要", "abstract", "关键词", "keywords", "参考文献", "references"]
    detect_patterns = [
        r"(?i)abstract",
        r"(?i)introduction",
        r"(?i)methodology",
        r"(?i)conclusion",
    ]

    def detect(self, text: str, metadata: dict = None) -> float:
        score = 0.0
        features = metadata or {}

        if features.get("has_citations"):
            score += 0.3

        first_3000 = text[:3000].lower()
        for kw in ["abstract", "摘要", "关键词", "keywords"]:
            if kw in first_3000:
                score += 0.15
                break

        last_2000 = text[-2000:].lower() if len(text) > 2000 else text.lower()
        for kw in ["references", "参考文献", "bibliography"]:
            if kw in last_2000:
                score += 0.15
                break

        for p in self.detect_patterns:
            if re.search(p, first_3000):
                score += 0.1
                break

        return min(score, 1.0)

    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        sections = self._split_by_section(text)
        chunks = []
        for i, section in enumerate(sections):
            section_chunks = self._split_content(section["content"])
            for j, chunk_text in enumerate(section_chunks):
                chunk_metadata = (metadata or {}).copy()
                chunk_metadata.update({
                    "section": section.get("title", ""),
                    "section_type": section.get("type", "content"),
                })
                chunks.append(ChunkResult(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    chunk_index=len(chunks),
                ))
        return chunks

    def _split_by_section(self, text: str) -> list:
        """按论文章节切分"""
        section_keywords = [
            (r"(?i)^(?:摘\s*要|abstract)", "abstract"),
            (r"(?i)^(?:引\s*言|introduction)", "introduction"),
            (r"(?i)^(?:方\s*法|methodology|methods)", "methodology"),
            (r"(?i)^(?:结\s*果|results)", "results"),
            (r"(?i)^(?:讨\s*论|discussion)", "discussion"),
            (r"(?i)^(?:结\s*论|conclusion)", "conclusion"),
            (r"(?i)^(?:参考文献|references|bibliography)", "references"),
        ]

        sections = []
        current_title = ""
        current_type = "content"
        current_content = []

        for line in text.split("\n"):
            stripped = line.strip()
            matched = False

            for pattern, stype in section_keywords:
                if re.match(pattern, stripped):
                    if current_content:
                        sections.append({
                            "title": current_title,
                            "type": current_type,
                            "content": "\n".join(current_content),
                        })
                    current_title = stripped
                    current_type = stype
                    current_content = []
                    matched = True
                    break

            if not matched:
                current_content.append(line)

        if current_content:
            sections.append({
                "title": current_title,
                "type": current_type,
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
