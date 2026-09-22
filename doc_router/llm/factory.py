"""LLM工厂 - 创建LLM实例"""
from typing import Optional, Dict, Any
from .base import BaseLLM

# 提供商映射
PROVIDER_MAP = {
    "ollama": "doc_router.llm.ollama.OllamaLLM",
    "openai": "doc_router.llm.openai.OpenAICompatibleLLM",
    "dashscope": "doc_router.llm.openai.OpenAICompatibleLLM",
    "zhipu": "doc_router.llm.openai.OpenAICompatibleLLM",
    "moonshot": "doc_router.llm.openai.OpenAICompatibleLLM",
    "deepseek": "doc_router.llm.openai.OpenAICompatibleLLM",
}


def create_llm(provider: str = "ollama", **kwargs) -> BaseLLM:
    """创建LLM实例
    
    Args:
        provider: 提供商名称 (ollama / openai / dashscope / zhipu / ...)
        **kwargs: 传递给LLM的参数
        
    Returns:
        BaseLLM实例
    """
    if provider not in PROVIDER_MAP:
        raise ValueError(f"不支持的提供商: {provider}，可用: {list(PROVIDER_MAP.keys())}")

    # 动态导入
    module_path, class_name = PROVIDER_MAP[provider].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    cls = getattr(module, class_name)

    # Ollama需要特殊处理
    if provider == "ollama":
        kwargs.setdefault("model", "qwen2:7b")
        kwargs.setdefault("base_url", "http://localhost:11434")
    else:
        # OpenAI兼容API
        kwargs.setdefault("provider", provider)

    return cls(**kwargs)


def create_llm_from_config(config: Dict[str, Any]) -> BaseLLM:
    """从配置创建LLM实例
    
    Args:
        config: LLM配置字典
        
    Returns:
        BaseLLM实例
    """
    provider = config.get("provider", "ollama")
    
    # 过滤出LLM相关的配置
    llm_config = {
        "model": config.get("model", ""),
        "api_key": config.get("api_key", ""),
        "base_url": config.get("base_url", ""),
        "timeout": config.get("timeout", 60),
    }
    
    # 对于OpenAI兼容API，添加provider
    if provider != "ollama":
        llm_config["provider"] = provider
    
    return create_llm(provider=provider, **llm_config)


def get_llm_providers() -> Dict[str, list]:
    """获取支持的LLM提供商和模型
    
    Returns:
        提供商和模型列表
    """
    from .openai import OpenAICompatibleLLM
    
    providers = {
        "ollama": {
            "name": "Ollama (本地)",
            "requires_api_key": False,
            "description": "本地部署的开源模型",
        },
        "openai": {
            "name": "OpenAI",
            "requires_api_key": True,
            "description": "GPT-4, GPT-3.5等",
        },
        "dashscope": {
            "name": "通义千问",
            "requires_api_key": True,
            "description": "阿里云通义千问系列模型",
        },
        "zhipu": {
            "name": "智谱AI",
            "requires_api_key": True,
            "description": "GLM系列模型",
        },
        "moonshot": {
            "name": "月之暗面",
            "requires_api_key": True,
            "description": "Kimi系列模型",
        },
        "deepseek": {
            "name": "DeepSeek",
            "requires_api_key": True,
            "description": "DeepSeek系列模型",
        },
    }
    
    return providers
