"""模板匹配引擎 - 根据文档特征匹配最佳模板"""
from typing import Optional
from ..templates.base import BaseTemplate
from ..core.detector import DocumentDetector


class TemplateMatcher:
    """模板匹配器"""

    def __init__(self):
        self.detector = DocumentDetector()
        self.templates: list[BaseTemplate] = []

    def register(self, template: BaseTemplate):
        """注册模板"""
        self.templates.append(template)

    def match(self, text: str, file_ext: str = "", metadata: dict = None) -> Optional[BaseTemplate]:
        """匹配最佳模板，返回模板实例"""
        features = self.detector.detect_features(text, file_ext)
        if metadata:
            features.update(metadata)

        best_template = None
        best_score = 0.0

        for template in self.templates:
            score = template.detect(text, features)
            if score > best_score:
                best_score = score
                best_template = template

        if best_template and best_score > 0.3:
            return best_template

        return None

    def match_all(self, text: str, file_ext: str = "", metadata: dict = None) -> list[tuple[BaseTemplate, float]]:
        """返回所有模板的匹配分数"""
        features = self.detector.detect_features(text, file_ext)
        if metadata:
            features.update(metadata)

        results = []
        for template in self.templates:
            score = template.detect(text, features)
            if score > 0:
                results.append((template, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results
