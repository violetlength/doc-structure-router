"""OCR模块 - 支持扫描版PDF文本提取"""
from .engine import BaseOCREngine, get_ocr_engine

__all__ = ["BaseOCREngine", "get_ocr_engine"]
