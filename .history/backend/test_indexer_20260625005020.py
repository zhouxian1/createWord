"""测试语义索引功能（跳过chromadb）"""
import sys
sys.path.insert(0, '.')

# 强制标记chromadb不可用
from app.services.semantic_indexer import SemanticIndexer
indexer = SemanticIndexer()
indexer._chroma_available = False  # 跳过chromadb

# 构建索引
result = indexer.build_index(
    file_id=999,
    text='这是一个测试文档，用于验证语义索引功能。软件开发计划是438C标准文档之一。软件测试计划包含测试策略和测试用例。',
    metadata={'knowledge_base_id': 1, 'filename': 'test.docx'},
    file_type='docx'
)
print(f'build_index result: {result}')
print(f'text_chunks count: {len(indexer._text_chunks)}')

# 搜索
results = indexer.search('软件开发计划', n_results=3, use_rerank=False)
print(f'search results: {len(results)}')
for r in results:
    content = r.get('content', '')[:100]
    score = r.get('score', 0)
    print(f'  score={score:.3f}, content: {content}')
