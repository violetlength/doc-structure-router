"""PgVector写入示例"""
import json
from doc_router import DocumentRouter


def main():
    import psycopg2
    from pgvector.psycopg2 import register_vector

    router = DocumentRouter()
    chunks = router.process_file("path/to/your/document.pdf")
    print(f"切分为 {len(chunks)} 个块")

    # 连接PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="vectordb",
        user="postgres",
        password="password",
    )
    register_vector(conn)
    cur = conn.cursor()

    # 创建表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id SERIAL PRIMARY KEY,
            text TEXT,
            metadata JSONB,
            embedding vector(1024)
        )
    """)
    conn.commit()

    # 写入（需要自己生成embedding）
    for c in chunks:
        # embedding = model.encode(c.text).tolist()
        cur.execute(
            "INSERT INTO knowledge_base (text, metadata, embedding) VALUES (%s, %s, %s)",
            (c.text, json.dumps(c.metadata, ensure_ascii=False), None),
        )

    conn.commit()
    print(f"完成，共写入 {len(chunks)} 条")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
