"""测试语义索引功能"""
from app.services.semantic_indexer import SemanticIndexer

indexer = SemanticIndexer()

# 构建索引
result = indexer.build_index(
    file_id=999,
    text='这是一个测试文档，用于验证语义索引功能。软件开发计划是438C标准文档之一。',
    metadata={'knowledge_base_id': 1, 'filename': 'test.docx'},
    file_type='docx'
)
print(f'build_index result: {result}')

# 搜索
results = indexer.search('软件开发计划', n_results=3, use_rerank=False)
print(f'search results: {len(results)}')
for r in results:
    content = r.get('content', '')[:100]
    print(f'  content: {content}')
