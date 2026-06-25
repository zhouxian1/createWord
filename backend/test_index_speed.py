"""测试索引构建速度"""
import os, sys, time
sys.path.insert(0, '.')

from app.services.semantic_indexer import SemanticIndexer

print("1. 初始化SemanticIndexer...")
t0 = time.time()
indexer = SemanticIndexer()
print(f"   耗时: {time.time()-t0:.1f}s, chroma_available={indexer._chroma_available}")

print("\n2. 构建索引...")
text = "软件开发计划是438C标准文档之一。" * 10
t0 = time.time()
result = indexer.build_index(
    file_id=888,
    text=text,
    metadata={'knowledge_base_id': 1, 'filename': 'test.docx'},
    file_type='docx'
)
print(f"   耗时: {time.time()-t0:.1f}s")
print(f"   结果: {result}")
print(f"   chroma_available: {indexer._chroma_available}")

print("\n3. 搜索...")
t0 = time.time()
results = indexer.search('软件开发计划', n_results=3, use_rerank=False)
print(f"   耗时: {time.time()-t0:.1f}s")
print(f"   结果数: {len(results)}")
for r in results:
    print(f"   score={r.get('score',0):.3f}, content={r.get('content','')[:60]}")

print("\n完成!")
