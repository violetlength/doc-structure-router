"""模板基类 - 所有文档模板继承此类"""
from abc import ABC, abstractmethod
from typing import List
from ..schemas.chunk import ChunkResult


class BaseTemplate(ABC):
    """文档模板基类"""

    name: str = "base"
    description: str = ""
    detect_keywords: list[str] = []
    detect_patterns: list[str] = []

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def detect(self, text: str, metadata: dict = None) -> float:
        """检测文档是否匹配此模板，返回置信度 0-1"""
        pass

    @abstractmethod
    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        """按模板逻辑切分文档"""
        pass

    def _overlap_split(self, chunks: List[str]) -> List[str]:
        """滑动窗口，保留重叠部分"""
        if self.chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks

        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            overlap_text = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            result.append(overlap_text + chunks[i])
        return result
