"""通用兜底模板 - 无法匹配其他模板时使用"""
import re
from typing import List
from .base import BaseTemplate
from ..schemas.chunk import ChunkResult


class FallbackTemplate(BaseTemplate):
    """通用兜底模板"""

    name = "fallback"
    description = "无法匹配其他模板时的通用处理"

    def detect(self, text: str, metadata: dict = None) -> float:
        return 0.5

    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        chunks = self._split_by_paragraph(text)
        results = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata["split_strategy"] = "paragraph"
            results.append(ChunkResult(
                text=chunk_text,
                metadata=chunk_metadata,
                chunk_index=i,
            ))
        return results

    def _split_by_paragraph(self, text: str) -> List[str]:
        """按段落切分"""
        paragraphs = re.split(r"\n\s*\n", text)
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

        return chunks if chunks else [text]
