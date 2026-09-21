"""Milvus写入示例"""
from doc_router import DocumentRouter


def main():
    from pymilvus import MilvusClient, DataType

    router = DocumentRouter()
    chunks = router.process_file("path/to/your/document.pdf")
    print(f"切分为 {len(chunks)} 个块")

    # 连接Milvus
    client = MilvusClient(uri="http://localhost:19530")

    # 创建集合
    schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("text", DataType.VARCHAR, max_length=8192)
    schema.add_field("metadata", DataType.JSON)
    schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=1024)

    index_params = client.prepare_index_params()
    index_params.add_index(field_name="embedding", metric_type="COSINE")

    collection_name = "knowledge_base"
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params,
    )

    # 写入（需要自己生成embedding）
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer("your-model-name")

    data = []
    for c in chunks:
        data.append({
            "text": c.text,
            "metadata": c.metadata,
            # "embedding": model.encode(c.text).tolist(),
        })

    client.insert(collection_name=collection_name, data=data)
    print(f"完成，共写入 {len(data)} 条")


if __name__ == "__main__":
    main()
