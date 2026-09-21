"""标准化输出数据结构"""
from dataclasses import dataclass, field
from typing import Optional
import hashlib
import time


@dataclass
class TemplateInfo:
    """模板匹配结果"""
    template_type: str
    confidence: float
    detect_rules_matched: list[str] = field(default_factory=list)


@dataclass
class ChunkResult:
    """切分后的标准输出块"""
    text: str
    metadata: dict = field(default_factory=dict)
    source: str = ""
    template_type: str = "fallback"
    chunk_index: int = 0
    confidence: float = 1.0

    def __post_init__(self):
        if "id" not in self.metadata:
            self.metadata["id"] = self._generate_id()
        if "doc_type" not in self.metadata:
            self.metadata["doc_type"] = self.template_type
        if "chunk_index" not in self.metadata:
            self.metadata["chunk_index"] = self.chunk_index
        if "source" not in self.metadata:
            self.metadata["source"] = self.source

    def _generate_id(self) -> str:
        content = f"{self.source}:{self.chunk_index}:{self.text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()

    @property
    def id(self) -> str:
        return self.metadata["id"]

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "metadata": self.metadata,
            "id": self.id,
        }
