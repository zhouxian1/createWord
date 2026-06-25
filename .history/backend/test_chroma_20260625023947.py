"""测试chromadb基本功能"""
print("1. 导入chromadb...")
try:
    import chromadb
    print(f"   chromadb version: {chromadb.__version__}")
except ImportError as e:
    print(f"   导入失败: {e}")
    exit(1)

print("2. 创建client...")
client = chromadb.PersistentClient(path='data/vector_db_test')

print("3. 创建collection...")
collection = client.get_or_create_collection(name="test", metadata={"hnsw:space": "cosine"})

print("4. 插入文档...")
collection.upsert(
    ids=["doc1", "doc2"],
    documents=["软件开发计划是438C标准文档之一", "软件测试计划包含测试策略和测试用例"],
    metadatas=[{"source": "test1"}, {"source": "test2"}]
)

print("5. 查询...")
results = collection.query(query_texts=["软件开发"], n_results=2)
print(f"   结果数: {len(results['ids'][0])}")
for i, doc in enumerate(results['documents'][0]):
    print(f"   [{i}] {doc[:80]}")

print("6. 测试完成!")
