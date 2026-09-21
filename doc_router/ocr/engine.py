"""OCR引擎 - 支持PaddleOCR和Tesseract"""
import os
from typing import Optional
from abc import ABC, abstractmethod


class BaseOCREngine(ABC):
    """OCR引擎基类"""

    @abstractmethod
    def extract_text_from_image(self, image_path: str) -> str:
        """从图片提取文本"""
        pass

    @abstractmethod
    def extract_text_from_pdf(self, pdf_path: str, pages: list[int] = None) -> str:
        """从PDF提取文本（先转图片再OCR）"""
        pass


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR引擎"""

    def __init__(self, lang: str = "ch", use_gpu: bool = False, **kwargs):
        try:
            from paddleocr import PaddleOCR
            # 尝试2.x API
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu, show_log=False, **kwargs)
            self.version = 2
        except TypeError:
            # 3.x API
            self.ocr = PaddleOCR(lang=lang, **kwargs)
            self.version = 3

    def extract_text_from_image(self, image_path: str) -> str:
        """从图片提取文本"""
        if self.version == 2:
            return self._extract_v2(image_path)
        else:
            return self._extract_v3(image_path)

    def _extract_v2(self, image_path: str) -> str:
        """PaddleOCR 2.x API"""
        result = self.ocr.ocr(image_path, cls=True)
        if not result or not result[0]:
            return ""

        lines = []
        for line in result[0]:
            if line[1]:
                text = line[1][0]
                confidence = line[1][1]
                if confidence > 0.5:
                    lines.append(text)
        return "\n".join(lines)

    def _extract_v3(self, image_path: str) -> str:
        """PaddleOCR 3.x API"""
        result = self.ocr.ocr(image_path)
        if not result or not result[0]:
            return ""

        lines = []
        for line in result[0]:
            if line[1]:
                text = line[1][0]
                confidence = line[1][1]
                if confidence > 0.5:
                    lines.append(text)
        return "\n".join(lines)

    def extract_text_from_pdf(self, pdf_path: str, pages: list[int] = None) -> str:
        """从PDF提取文本（先转图片再OCR）"""
        try:
            import pymupdf
        except ImportError:
            try:
                import fitz as pymupdf
            except ImportError:
                raise ImportError(
                    "需要安装 PyMuPDF: pip install PyMuPDF"
                )

        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)

        if pages is None:
            pages = list(range(total_pages))
        else:
            pages = [p for p in pages if 0 <= p < total_pages]

        all_text = []
        for page_idx in pages:
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=200)

            # 保存为临时文件
            temp_path = f"_temp_page_{page_idx}.png"
            pix.save(temp_path)

            try:
                text = self.extract_text_from_image(temp_path)
                if text.strip():
                    all_text.append(f"[第{page_idx + 1}页]\n{text}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        doc.close()
        return "\n\n".join(all_text)


class TesseractOCREngine(BaseOCREngine):
    """Tesseract引擎"""

    def __init__(self, lang: str = "chi_sim+eng"):
        try:
            import pytesseract
            from PIL import Image
            self.pytesseract = pytesseract
            self.Image = Image
            self.lang = lang
        except ImportError:
            raise ImportError(
                "需要安装 Tesseract: pip install pytesseract Pillow"
            )

    def extract_text_from_image(self, image_path: str) -> str:
        """从图片提取文本"""
        img = self.Image.open(image_path)
        text = self.pytesseract.image_to_string(img, lang=self.lang)
        return text.strip()

    def extract_text_from_pdf(self, pdf_path: str, pages: list[int] = None) -> str:
        """从PDF提取文本"""
        try:
            import pymupdf
        except ImportError:
            try:
                import fitz as pymupdf
            except ImportError:
                raise ImportError(
                    "需要安装 PyMuPDF: pip install PyMuPDF"
                )

        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)

        if pages is None:
            pages = list(range(total_pages))
        else:
            pages = [p for p in pages if 0 <= p < total_pages]

        all_text = []
        for page_idx in pages:
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=200)

            temp_path = f"_temp_page_{page_idx}.png"
            pix.save(temp_path)

            try:
                text = self.extract_text_from_image(temp_path)
                if text.strip():
                    all_text.append(f"[第{page_idx + 1}页]\n{text}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        doc.close()
        return "\n\n".join(all_text)


def get_ocr_engine(engine: str = "paddle", **kwargs) -> BaseOCREngine:
    """
    获取OCR引擎实例

    Args:
        engine: OCR引擎类型，支持 "paddle" 或 "tesseract"
        **kwargs: 引擎参数

    Returns:
        OCR引擎实例
    """
    if engine == "paddle":
        return PaddleOCREngine(**kwargs)
    elif engine == "tesseract":
        return TesseractOCREngine(**kwargs)
    else:
        raise ValueError(f"不支持的OCR引擎: {engine}，支持 'paddle' 或 'tesseract'")
