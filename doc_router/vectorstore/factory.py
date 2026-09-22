"""向量库工厂"""
from typing import Optional, Dict, Any
from .base import BaseVectorStore

# 向量库类型映射
VECTORSTORE_MAP = {
    "chromadb": "doc_router.vectorstore.chromadb.ChromaDBStore",
}


def create_vectorstore(
    vector_db_type: str = "chromadb",
    collection: str = "documents",
    **kwargs,
) -> BaseVectorStore:
    """创建向量库实例
    
    Args:
        vector_db_type: 向量库类型
        collection: 集合名称
        **kwargs: 其他参数
        
    Returns:
        BaseVectorStore实例
    """
    if vector_db_type not in VECTORSTORE_MAP:
        raise ValueError(f"不支持的向量库类型: {vector_db_type}，可用: {list(VECTORSTORE_MAP.keys())}")

    # 动态导入
    module_path, class_name = VECTORSTORE_MAP[vector_db_type].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    cls = getattr(module, class_name)

    return cls(collection=collection, **kwargs)


def create_vectorstore_from_config(config: Dict[str, Any]) -> BaseVectorStore:
    """从配置创建向量库实例
    
    Args:
        config: 向量库配置字典
        
    Returns:
        BaseVectorStore实例
    """
    vector_db_type = config.get("type", "chromadb")
    
    # 过滤出向量库相关的配置
    vs_config = {
        "collection": config.get("collection", "documents"),
        "path": config.get("path", "./data/chroma_db"),
        "host": config.get("host", ""),
        "port": config.get("port", 0),
    }
    
    return create_vectorstore(vector_db_type=vector_db_type, **vs_config)


def get_vectorstore_types() -> Dict[str, dict]:
    """获取支持的向量库类型
    
    Returns:
        向量库类型和信息
    """
    return {
        "chromadb": {
            "name": "ChromaDB",
            "description": "轻量级本地向量库，适合开发和测试",
            "requires_server": False,
            "supports_persistence": True,
        },
    }
