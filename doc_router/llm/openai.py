"""OpenAI兼容LLM适配器

支持所有OpenAI兼容API：
- OpenAI (GPT-4, GPT-3.5)
- 通义千问 (DashScope)
- 智谱AI (GLM)
- 百度文心一言
- 其他兼容API
"""
from typing import Optional, List, Dict
from .base import BaseLLM, LLMResponse

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class OpenAICompatibleLLM(BaseLLM):
    """OpenAI兼容LLM适配器"""

    # 预设的API地址
    PRESETS = {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        },
        "dashscope": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": ["qwen-plus", "qwen-turbo", "qwen-max"],
        },
        "zhipu": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4", "glm-4-flash", "glm-3-turbo"],
        },
        "moonshot": {
            "base_url": "https://api.moonshot.cn/v1",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-coder"],
        },
    }

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: str = "",
        base_url: str = "",
        provider: str = "",
        **kwargs,
    ):
        # 根据provider设置base_url
        if provider and provider in self.PRESETS and not base_url:
            base_url = self.PRESETS[provider]["base_url"]
        
        if not base_url:
            base_url = "https://api.openai.com/v1"

        super().__init__(model=model, api_key=api_key, base_url=base_url, **kwargs)
        self.api_url = f"{base_url}/chat/completions"

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _call_with_httpx(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """使用httpx调用"""
        import httpx
        
        data = {
            "model": self.model,
            "messages": messages,
        }
        
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["max_tokens"] = kwargs["max_tokens"]

        with httpx.Client(timeout=kwargs.get("timeout", 60)) as client:
            response = client.post(
                self.api_url,
                headers=self._get_headers(),
                json=data,
            )
            response.raise_for_status()
            result = response.json()

        choice = result.get("choices", [{}])[0]
        usage = result.get("usage", {})

        return LLMResponse(
            content=choice.get("message", {}).get("content", ""),
            model=result.get("model", self.model),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            finish_reason=choice.get("finish_reason", ""),
            raw_response=result,
        )

    def _call_with_requests(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """使用requests调用"""
        import requests
        
        data = {
            "model": self.model,
            "messages": messages,
        }
        
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["max_tokens"] = kwargs["max_tokens"]

        response = requests.post(
            self.api_url,
            headers=self._get_headers(),
            json=data,
            timeout=kwargs.get("timeout", 60),
        )
        response.raise_for_status()
        result = response.json()

        choice = result.get("choices", [{}])[0]
        usage = result.get("usage", {})

        return LLMResponse(
            content=choice.get("message", {}).get("content", ""),
            model=result.get("model", self.model),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            finish_reason=choice.get("finish_reason", ""),
            raw_response=result,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """调用API"""
        call_kwargs = {
            "timeout": kwargs.get("timeout", self.config.get("timeout", 60)),
        }
        if temperature is not None:
            call_kwargs["temperature"] = temperature
        if max_tokens is not None:
            call_kwargs["max_tokens"] = max_tokens

        if HAS_HTTPX:
            return self._call_with_httpx(messages, **call_kwargs)
        elif HAS_REQUESTS:
            return self._call_with_requests(messages, **call_kwargs)
        else:
            raise ImportError("需要安装 httpx 或 requests: pip install httpx requests")

    @classmethod
    def get_preset_providers(cls) -> Dict[str, dict]:
        """获取预设的提供商信息"""
        return cls.PRESETS.copy()
