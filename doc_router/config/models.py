"""配置数据模型"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "ollama"           # ollama / openai / dashscope / zhipu
    model: str = "qwen2:7b"           # 模型名称
    api_key: str = ""                  # API密钥
    base_url: str = "http://localhost:11434/v1"  # API地址
    temperature: float = 0.7           # 温度
    max_tokens: int = 4096            # 最大token数
    timeout: int = 60                  # 超时时间(秒)

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }


@dataclass
class OCRConfig:
    """OCR配置"""
    engine: str = "paddle"             # paddle / tesseract
    lang: str = "ch"                   # 语言
    dpi: int = 200                     # DPI
    use_gpu: bool = False              # 是否使用GPU

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "lang": self.lang,
            "dpi": self.dpi,
            "use_gpu": self.use_gpu,
        }


@dataclass
class VectorDBConfig:
    """向量库配置"""
    type: str = "chromadb"             # chromadb / milvus / pgvector
    path: str = "./data/chroma_db"     # 存储路径
    collection: str = "documents"      # 集合名称
    host: str = "localhost"            # 主机(远程)
    port: int = 5432                   # 端口(远程)
    username: str = ""                 # 用户名(远程)
    password: str = ""                 # 密码(远程)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "path": self.path,
            "collection": self.collection,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }


@dataclass
class AnalysisConfig:
    """分析配置"""
    sample_pages: int = 50             # 样本分析页数
    chunk_size: int = 800              # 分块大小
    chunk_overlap: int = 150           # 分块重叠

    def to_dict(self) -> dict:
        return {
            "sample_pages": self.sample_pages,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }


@dataclass
class Config:
    """主配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    def to_dict(self) -> dict:
        return {
            "llm": self.llm.to_dict(),
            "ocr": self.ocr.to_dict(),
            "vector_db": self.vector_db.to_dict(),
            "analysis": self.analysis.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """从字典创建配置"""
        config = cls()
        
        if "llm" in data:
            config.llm = LLMConfig(**data["llm"])
        if "ocr" in data:
            config.ocr = OCRConfig(**data["ocr"])
        if "vector_db" in data:
            config.vector_db = VectorDBConfig(**data["vector_db"])
        if "analysis" in data:
            config.analysis = AnalysisConfig(**data["analysis"])
        
        return config
