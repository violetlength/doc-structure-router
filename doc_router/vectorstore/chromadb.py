"""ChromaDB向量库适配器"""
from typing import Optional, List, Dict, Any
from .base import BaseVectorStore, SearchResult

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


class ChromaDBStore(BaseVectorStore):
    """ChromaDB向量库适配器"""

    def __init__(
        self,
        collection: str = "documents",
        path: str = "./data/chroma_db",
        host: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(collection=collection, path=path, host=host, port=port, **kwargs)
        
        if not HAS_CHROMADB:
            raise ImportError("需要安装 chromadb: pip install chromadb")

        # 创建客户端
        if host and port:
            # 远程连接
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            # 本地持久化
            self.client = chromadb.PersistentClient(path=path)

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[list]] = None,
    ) -> List[str]:
        """添加文档"""
        if not texts:
            return []

        # 自动生成ID
        if ids is None:
            import hashlib
            ids = [
                hashlib.md5(f"{i}:{text[:100]}".encode()).hexdigest()
                for i, text in enumerate(texts)
            ]

        # 添加文档
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )

        return ids

    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
        embedding: Optional[list] = None,
    ) -> List[SearchResult]:
        """搜索"""
        results = self.collection.query(
            query_texts=[query] if not embedding else None,
            query_embeddings=[embedding] if embedding else None,
            n_results=k,
            where=filter,
        )

        search_results = []
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"][0]):
                search_results.append(
                    SearchResult(
                        id=doc_id,
                        text=results["documents"][0][i] if results.get("documents") else "",
                        metadata=results["metadatas"][0][i] if results.get("metadatas") else {},
                        score=1 - results["distances"][0][i] if results.get("distances") else 0,
                    )
                )

        return search_results

    def delete(self, ids: Optional[List[str]] = None, filter: Optional[dict] = None) -> bool:
        """删除文档"""
        try:
            if ids:
                self.collection.delete(ids=ids)
            elif filter:
                self.collection.delete(where=filter)
            return True
        except Exception as e:
            print(f"删除失败: {e}")
            return False

    def get(self, ids: Optional[List[str]] = None, filter: Optional[dict] = None) -> List[dict]:
        """获取文档"""
        results = self.collection.get(ids=ids, where=filter)
        
        documents = []
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"]):
                documents.append({
                    "id": doc_id,
                    "text": results["documents"][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][i] if results.get("metadatas") else {},
                })
        
        return documents

    def count(self) -> int:
        """获取文档数量"""
        return self.collection.count()

    def get_collection_info(self) -> dict:
        """获取集合信息"""
        return {
            "name": self.collection_name,
            "count": self.count(),
            "metadata": self.collection.metadata,
        }

    def peek(self, limit: int = 5) -> List[dict]:
        """预览文档"""
        results = self.collection.peek(limit=limit)
        
        documents = []
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"]):
                documents.append({
                    "id": doc_id,
                    "text": results["documents"][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][i] if results.get("metadatas") else {},
                })
        
        return documents

    def reset(self) -> bool:
        """重置集合"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            return True
        except Exception as e:
            print(f"重置失败: {e}")
            return False
