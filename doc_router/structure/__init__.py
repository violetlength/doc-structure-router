"""文档结构模块 - 识别和提取文档结构"""
from .detector import StructureDetector
from .models import DocumentStructure, TOCItem, HeadingNode

__all__ = ["StructureDetector", "DocumentStructure", "TOCItem", "HeadingNode"]
