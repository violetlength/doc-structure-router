"""切分器基类"""
from abc import ABC, abstractmethod
from typing import List
import re


class BaseSplitter(ABC):
    """文本切分器基类"""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """切分文本，返回块列表"""
        pass

    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """合并过小的块"""
        if not chunks:
            return chunks

        result = []
        current = ""
        for chunk in chunks:
            if len(current) + len(chunk) <= self.chunk_size:
                current = current + "\n\n" + chunk if current else chunk
            else:
                if current:
                    result.append(current)
                current = chunk
        if current:
            result.append(current)
        return result

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """添加重叠"""
        if self.chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks

        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            overlap = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            result.append(overlap + "\n" + chunks[i])
        return result
