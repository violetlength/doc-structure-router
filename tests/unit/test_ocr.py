"""OCR模块单元测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestOCREngine:
    """测试OCR引擎"""

    def test_get_ocr_engine_paddle(self):
        """测试获取PaddleOCR引擎"""
        from doc_router.ocr import get_ocr_engine

        with patch("doc_router.ocr.engine.PaddleOCREngine.__init__", return_value=None):
            engine = get_ocr_engine("paddle")
            assert engine is not None

    def test_get_ocr_engine_tesseract(self):
        """测试获取Tesseract引擎"""
        from doc_router.ocr import get_ocr_engine

        with patch("doc_router.ocr.engine.TesseractOCREngine.__init__", return_value=None):
            engine = get_ocr_engine("tesseract")
            assert engine is not None

    def test_get_ocr_engine_invalid(self):
        """测试获取无效OCR引擎"""
        from doc_router.ocr import get_ocr_engine

        with pytest.raises(ValueError, match="不支持的OCR引擎"):
            get_ocr_engine("invalid")


class TestPaddleOCREngine:
    """测试PaddleOCR引擎"""

    def test_init_without_paddleocr(self):
        """测试未安装PaddleOCR时初始化"""
        import sys
        # 保存原始模块
        original = sys.modules.get("paddleocr")
        try:
            sys.modules["paddleocr"] = None
            from doc_router.ocr.engine import PaddleOCREngine
            # 重新导入以清除缓存
            import importlib
            import doc_router.ocr.engine
            importlib.reload(doc_router.ocr.engine)

            with pytest.raises((ImportError, TypeError)):
                doc_router.ocr.engine.PaddleOCREngine()
        finally:
            # 恢复原始模块
            if original is not None:
                sys.modules["paddleocr"] = original
            else:
                sys.modules.pop("paddleocr", None)


class TestTesseractOCREngine:
    """测试Tesseract引擎"""

    def test_init_without_tesseract(self):
        """测试未安装Tesseract时初始化"""
        with patch.dict("sys.modules", {"pytesseract": None, "PIL": None}):
            from doc_router.ocr.engine import TesseractOCREngine

            with pytest.raises(ImportError, match="需要安装 Tesseract"):
                TesseractOCREngine()


class TestRouterOCR:
    """测试路由器OCR集成"""

    def test_router_init_with_ocr_params(self):
        """测试路由器初始化OCR参数"""
        from doc_router import DocumentRouter

        router = DocumentRouter(
            ocr_engine="paddle",
            ocr_lang="ch",
        )
        assert router.ocr_engine == "paddle"
        assert router.ocr_lang == "ch"

    def test_router_default_ocr_params(self):
        """测试路由器默认OCR参数"""
        from doc_router import DocumentRouter

        router = DocumentRouter()
        assert router.ocr_engine == "paddle"
        assert router.ocr_lang == "ch"

    def test_extract_text_from_pdf_no_ocr(self):
        """测试从PDF提取文本（无OCR时）"""
        from doc_router.core.router import DocumentRouter

        router = DocumentRouter()

        with patch.object(router, "_extract_text_from_pdf", return_value="提取的文本"):
            text = router._read_pdf("test.pdf")
            assert text == "提取的文本"

    def test_ocr_pdf_fallback(self):
        """测试OCR回退"""
        from doc_router.core.router import DocumentRouter

        router = DocumentRouter()

        with patch.object(router, "_extract_text_from_pdf", return_value=""):
            with patch.object(router, "_ocr_pdf", return_value="OCR文本"):
                text = router._read_pdf("test.pdf")
                assert text == "OCR文本"

    def test_ocr_pdf_import_error(self):
        """测试OCR依赖未安装时的错误提示"""
        from doc_router.core.router import DocumentRouter

        router = DocumentRouter()

        with patch.object(router, "_extract_text_from_pdf", return_value=""):
            with patch("doc_router.ocr.get_ocr_engine", side_effect=ImportError("未安装")):
                with pytest.raises(ImportError, match="需要安装OCR依赖"):
                    router._ocr_pdf("test.pdf")
