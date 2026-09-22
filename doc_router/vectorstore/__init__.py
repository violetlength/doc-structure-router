"""向量库适配器模块"""
from .base import BaseVectorStore, SearchResult
from .factory import create_vectorstore, get_vectorstore_types

__all__ = ["BaseVectorStore", "SearchResult", "create_vectorstore", "get_vectorstore_types"]
