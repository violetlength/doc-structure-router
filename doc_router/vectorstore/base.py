"""向量库基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    text: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata,
            "score": self.score,
        }


class BaseVectorStore(ABC):
    """向量库基类"""

    def __init__(self, collection: str = "documents", **kwargs):
        self.collection_name = collection
        self.config = kwargs

    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[list]] = None,
    ) -> List[str]:
        """添加文档
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            ids: ID列表
            embeddings: 向量列表
            
        Returns:
            ID列表
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
        embedding: Optional[list] = None,
    ) -> List[SearchResult]:
        """搜索
        
        Args:
            query: 查询文本
            k: 返回数量
            filter: 过滤条件
            embedding: 查询向量
            
        Returns:
            搜索结果列表
        """
        pass

    @abstractmethod
    def delete(self, ids: Optional[List[str]] = None, filter: Optional[dict] = None) -> bool:
        """删除文档
        
        Args:
            ids: ID列表
            filter: 过滤条件
            
        Returns:
            是否成功
        """
        pass

    @abstractmethod
    def get(self, ids: Optional[List[str]] = None, filter: Optional[dict] = None) -> List[dict]:
        """获取文档
        
        Args:
            ids: ID列表
            filter: 过滤条件
            
        Returns:
            文档列表
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """获取文档数量"""
        pass

    @abstractmethod
    def get_collection_info(self) -> dict:
        """获取集合信息"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(collection={self.collection_name})"
