"""文档结构数据模型"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class StructureType(str, Enum):
    """文档结构类型"""
    TOC = "toc"              # 目录型 - 有目录+页码
    CHAPTER = "chapter"      # 章节型 - 有章节编号
    HEADING = "heading"      # 分级标题型 - # ## ###
    GLOSSARY = "glossary"    # 词汇表型 - 术语+解释
    QA = "qa"                # 问答型 - 问题+答案
    REFERENCE = "reference"  # 参考文献型
    PLAIN = "plain"          # 纯文本 - 无特殊结构


@dataclass
class TOCItem:
    """目录条目"""
    title: str                          # 章节标题
    level: int = 1                      # 层级 (1=一级标题, 2=二级标题, ...)
    page: int = 0                       # 起始页码
    end_page: Optional[int] = None      # 结束页码 (None表示到下一个同级或文档末尾)
    children: list["TOCItem"] = field(default_factory=list)  # 子章节

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "level": self.level,
            "page": self.page,
            "end_page": self.end_page,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class HeadingNode:
    """分级标题节点"""
    title: str                          # 标题文本
    level: int                          # 层级 (# = 1, ## = 2, ### = 3)
    content: str = ""                   # 该标题下的内容
    children: list["HeadingNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "level": self.level,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class DocumentStructure:
    """文档结构"""
    structure_type: StructureType       # 结构类型
    toc: list[TOCItem] = field(default_factory=list)     # 目录结构
    headings: list[HeadingNode] = field(default_factory=list)  # 分级标题结构
    metadata: dict = field(default_factory=dict)         # 额外元数据
    confidence: float = 0.0             # 识别置信度 0-1

    def to_dict(self) -> dict:
        return {
            "structure_type": self.structure_type.value,
            "toc": [item.to_dict() for item in self.toc],
            "headings": [h.to_dict() for h in self.headings],
            "metadata": self.metadata,
            "confidence": self.confidence,
        }

    def get_flat_toc(self) -> list[TOCItem]:
        """获取扁平化的目录列表（按页码排序）"""
        items = []
        for item in self.toc:
            items.append(item)
            items.extend(self._flatten_children(item))
        return sorted(items, key=lambda x: x.page)

    def _flatten_children(self, item: TOCItem) -> list[TOCItem]:
        """递归展平子目录"""
        items = []
        for child in item.children:
            items.append(child)
            items.extend(self._flatten_children(child))
        return items
