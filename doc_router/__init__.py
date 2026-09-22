"""
doc-structure-router
文档结构智能路由 - 自动检测文档结构，选择最佳切分策略
"""
from .core.router import DocumentRouter
from .core.detector import DocumentDetector
from .core.matcher import TemplateMatcher
from .schemas.chunk import ChunkResult, TemplateInfo
from .templates.base import BaseTemplate
from .ocr import BaseOCREngine, get_ocr_engine
from .structure import StructureDetector, DocumentStructure, TOCItem, HeadingNode

__version__ = "0.1.0"
__author__ = "doc-structure-router"

__all__ = [
    "DocumentRouter",
    "DocumentDetector",
    "TemplateMatcher",
    "ChunkResult",
    "TemplateInfo",
    "BaseTemplate",
    "BaseOCREngine",
    "get_ocr_engine",
    "StructureDetector",
    "DocumentStructure",
    "TOCItem",
    "HeadingNode",
]
