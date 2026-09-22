"""LLM基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str                    # 响应内容
    model: str = ""                 # 使用的模型
    usage: dict = field(default_factory=dict)  # token使用情况
    finish_reason: str = ""         # 结束原因
    raw_response: Any = None        # 原始响应对象

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
        }


class BaseLLM(ABC):
    """LLM基类"""

    def __init__(self, model: str = "", api_key: str = "", base_url: str = "", **kwargs):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.config = kwargs

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度
            max_tokens: 最大token数
            
        Returns:
            LLMResponse对象
        """
        pass

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """补全接口（简化对话）
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度
            max_tokens: 最大token数
            
        Returns:
            LLMResponse对象
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    def analyze_document(self, text: str, task: str = "summarize", **kwargs) -> LLMResponse:
        """分析文档
        
        Args:
            text: 文档内容
            task: 分析任务 (summarize / structure / extract_keywords)
            
        Returns:
            LLMResponse对象
        """
        prompts = {
            "summarize": "请简要总结以下文档的主要内容：",
            "structure": "请分析以下文档的结构，包括章节划分和主要主题：",
            "extract_keywords": "请提取以下文档的关键词和主要概念：",
        }
        
        system_prompt = "你是一个专业的文档分析助手。"
        prompt = f"{prompts.get(task, prompts['summarize'])}\n\n{text}"
        
        return self.complete(prompt, system_prompt=system_prompt, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"
