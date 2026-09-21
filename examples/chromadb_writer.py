"""ChromaDB写入示例"""
import chromadb
from doc_router import DocumentRouter


def main():
    router = DocumentRouter()

    # 1. 处理文档
    chunks = router.process_file("path/to/your/document.pdf")
    print(f"切分为 {len(chunks)} 个块")

    # 2. 连接ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="knowledge_base",
        metadata={"hnsw:space": "cosine"},
    )

    # 3. 批量写入
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.add(
            documents=[c.text for c in batch],
            metadatas=[c.metadata for c in batch],
            ids=[c.id for c in batch],
        )
        print(f"写入 {len(batch)} 个块")

    print(f"完成，共写入 {collection.count()} 个块")


if __name__ == "__main__":
    main()
