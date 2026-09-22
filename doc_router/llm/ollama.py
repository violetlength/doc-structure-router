"""Ollama LLM适配器"""
import json
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


class OllamaLLM(BaseLLM):
    """Ollama LLM适配器
    
    支持本地部署的Ollama服务
    """

    def __init__(
        self,
        model: str = "qwen2:7b",
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        super().__init__(model=model, base_url=base_url, **kwargs)
        self.api_url = f"{base_url}/api/chat"

    def _call_with_httpx(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """使用httpx调用"""
        import httpx
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        
        # 添加可选参数
        if "temperature" in kwargs:
            data["options"] = data.get("options", {})
            data["options"]["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["options"] = data.get("options", {})
            data["options"]["num_predict"] = kwargs["max_tokens"]

        with httpx.Client(timeout=kwargs.get("timeout", 60)) as client:
            response = client.post(self.api_url, json=data)
            response.raise_for_status()
            result = response.json()

        return LLMResponse(
            content=result.get("message", {}).get("content", ""),
            model=result.get("model", self.model),
            usage={
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0),
            },
            finish_reason="stop" if result.get("done") else "length",
            raw_response=result,
        )

    def _call_with_requests(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """使用requests调用"""
        import requests
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        
        if "temperature" in kwargs:
            data["options"] = data.get("options", {})
            data["options"]["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["options"] = data.get("options", {})
            data["options"]["num_predict"] = kwargs["max_tokens"]

        response = requests.post(
            self.api_url,
            json=data,
            timeout=kwargs.get("timeout", 60),
        )
        response.raise_for_status()
        result = response.json()

        return LLMResponse(
            content=result.get("message", {}).get("content", ""),
            model=result.get("model", self.model),
            usage={
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0),
            },
            finish_reason="stop" if result.get("done") else "length",
            raw_response=result,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """调用Ollama API"""
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

    def list_models(self) -> List[str]:
        """列出可用模型"""
        try:
            if HAS_HTTPX:
                import httpx
                with httpx.Client(timeout=10) as client:
                    response = client.get(f"{self.base_url}/api/tags")
                    response.raise_for_status()
                    result = response.json()
                    return [m["name"] for m in result.get("models", [])]
            elif HAS_REQUESTS:
                import requests
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                response.raise_for_status()
                result = response.json()
                return [m["name"] for m in result.get("models", [])]
        except Exception:
            pass
        return []
