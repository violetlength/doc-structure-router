"""LLM文档结构分析器"""
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .llm.base import BaseLLM, LLMResponse
from .llm.factory import create_llm_from_config
from .config.models import LLMConfig


@dataclass
class StructureAnalysisResult:
    """结构分析结果"""
    structure_type: str           # 文档结构类型
    confidence: float             # 置信度 0-1
    description: str              # 描述
    key_sections: list            # 主要章节/部分
    suggested_template: str       # 建议使用的模板
    raw_response: str             # LLM原始响应

    def to_dict(self) -> dict:
        return {
            "structure_type": self.structure_type,
            "confidence": self.confidence,
            "description": self.description,
            "key_sections": self.key_sections,
            "suggested_template": self.suggested_template,
        }


# 结构类型到模板的映射
STRUCTURE_TEMPLATE_MAP = {
    "toc": "toc_based",
    "目录型": "toc_based",
    "chapter": "textbook",
    "章节型": "textbook",
    "glossary": "dictionary",
    "词汇表型": "dictionary",
    "qa": "guide",
    "问答型": "guide",
    "reference": "paper",
    "参考文档": "paper",
    "plain": "fallback",
    "平面文档": "fallback",
}


class StructureAnalyzer:
    """使用LLM分析文档结构"""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Args:
            llm_config: LLM配置，None则从配置文件读取
        """
        if llm_config is None:
            from .config.manager import ConfigManager
            manager = ConfigManager()
            config = manager.load()
            llm_config = config.llm
        
        self.llm = create_llm_from_config(llm_config.to_dict())

    def analyze(self, text: str, sample_size: int = 2000) -> StructureAnalysisResult:
        """分析文档结构
        
        Args:
            text: 文档文本内容
            sample_size: 采样大小（字符数）
            
        Returns:
            StructureAnalysisResult对象
        """
        # 采样文本
        sample_text = text[:sample_size] if len(text) > sample_size else text
        
        # 构建提示词
        system_prompt = """你是一个专业的文档结构分析助手。你的任务是分析文档内容，识别其结构类型。

可选的结构类型：
1. toc (目录型) - 有目录、书签的文档，如书籍、手册
2. chapter (章节型) - 有章节编号的文档，如教材、技术文档
3. glossary (词汇表型) - 术语+解释格式的文档，如词典、手册
4. qa (问答型) - 问题+答案格式的文档，如FAQ、考试题
5. reference (参考文档) - API文档、规范文档
6. plain (平面文档) - 无明显结构的纯文本文档

请分析文档内容，返回JSON格式的结果：
{
    "structure_type": "类型英文名",
    "confidence": 0.85,
    "description": "简要描述文档结构特点",
    "key_sections": ["主要章节1", "主要章节2"],
    "reasoning": "分析理由"
}

注意：
- confidence范围0-1，表示你对判断的确信程度
- key_sections列出文档中识别到的主要部分
- reasoning解释你为什么做出这个判断"""

        user_prompt = f"""请分析以下文档的结构类型：

{sample_text}

请返回JSON格式的分析结果。"""

        # 调用LLM
        response = self.llm.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # 低温度，更稳定的输出
        )

        # 解析响应
        return self._parse_response(response)

    def _parse_response(self, response: LLMResponse) -> StructureAnalysisResult:
        """解析LLM响应"""
        import json
        import re
        
        content = response.content
        
        # 尝试提取JSON
        try:
            # 尝试直接解析
            result = json.loads(content)
        except json.JSONDecodeError:
            # 尝试从文本中提取JSON
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError:
                    # 解析失败，返回默认值
                    return StructureAnalysisResult(
                        structure_type="plain",
                        confidence=0.5,
                        description="无法解析LLM响应",
                        key_sections=[],
                        suggested_template="fallback",
                        raw_response=content,
                    )
            else:
                return StructureAnalysisResult(
                    structure_type="plain",
                    confidence=0.5,
                    description="无法解析LLM响应",
                    key_sections=[],
                    suggested_template="fallback",
                    raw_response=content,
                )

        # 提取字段
        structure_type = result.get("structure_type", "plain")
        confidence = float(result.get("confidence", 0.5))
        description = result.get("description", "")
        key_sections = result.get("key_sections", [])
        
        # 映射到模板
        suggested_template = STRUCTURE_TEMPLATE_MAP.get(structure_type, "fallback")

        return StructureAnalysisResult(
            structure_type=structure_type,
            confidence=confidence,
            description=description,
            key_sections=key_sections,
            suggested_template=suggested_template,
            raw_response=content,
        )

    def analyze_with_llm(self, text: str, llm: BaseLLM, sample_size: int = 2000) -> StructureAnalysisResult:
        """使用指定的LLM分析文档结构
        
        Args:
            text: 文档文本内容
            llm: LLM实例
            sample_size: 采样大小
            
        Returns:
            StructureAnalysisResult对象
        """
        # 临时使用指定的LLM
        original_llm = self.llm
        self.llm = llm
        
        try:
            return self.analyze(text, sample_size)
        finally:
            self.llm = original_llm
