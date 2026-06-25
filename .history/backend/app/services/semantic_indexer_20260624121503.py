"""语义索引服务 - 构建文档的语义向量索引"""
import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SemanticIndexer:
    """语义索引构建器 - 支持文档分块、向量化、索引存储"""

    def __init__(self, db_path=None, embedding_model=None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vector_db')
        self.embedding_model = embedding_model
        self._collection = None

    def _get_collection(self, collection_name='documents'):
        """获取或创建向量集合"""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.db_path)
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return collection
        except ImportError:
            logger.warning("chromadb未安装，语义索引功能不可用")
            return None

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
        """将文本分块"""
        if not text or not text.strip():
            return []

        chunks = []
        paragraphs = text.split('\n\n')

        current_chunk = ""
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    'index': chunk_index,
                    'content': current_chunk.strip(),
                    'char_count': len(current_chunk.strip())
                })
                chunk_index += 1
                # 保留overlap
                if overlap > 0:
                    words = current_chunk.split()
                    overlap_text = ' '.join(words[-overlap // 2:]) if len(words) > overlap // 2 else ''
                    current_chunk = overlap_text + '\n\n' + para
                else:
                    current_chunk = para
            else:
                current_chunk = current_chunk + '\n\n' + para if current_chunk else para

        if current_chunk.strip():
            chunks.append({
                'index': chunk_index,
                'content': current_chunk.strip(),
                'char_count': len(current_chunk.strip())
            })

        return chunks

    def build_index(self, file_id: int, text: str, metadata: Dict = None):
        """为文档构建语义索引"""
        collection = self._get_collection()
        if collection is None:
            return {'chunk_count': 0, 'status': 'skipped'}

        chunks = self.chunk_text(text)
        if not chunks:
            return {'chunk_count': 0, 'status': 'empty'}

        try:
            ids = [f"file_{file_id}_chunk_{chunk['index']}" for chunk in chunks]
            documents = [chunk['content'] for chunk in chunks]
            metas = []
            for chunk in chunks:
                meta = {'file_id': file_id, 'chunk_index': chunk['index'],
                        'char_count': chunk['char_count']}
                if metadata:
                    meta.update(metadata)
                metas.append(meta)

            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metas
            )

            return {'chunk_count': len(chunks), 'status': 'completed'}
        except Exception as e:
            logger.error(f"构建索引失败: {str(e)}")
            return {'chunk_count': 0, 'status': 'error', 'error': str(e)}

    def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None) -> List[Dict]:
        """语义搜索"""
        collection = self._get_collection()
        if collection is None:
            return []

        try:
            kwargs = {'query_texts': [query], 'n_results': n_results}
            if filter_metadata:
                kwargs['where'] = filter_metadata

            results = collection.query(**kwargs)

            search_results = []
            for i in range(len(results['ids'][0])):
                search_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

            return search_results
        except Exception as e:
            logger.error(f"语义搜索失败: {str(e)}")
            return []

    def delete_index(self, file_id: int):
        """删除文档索引"""
        collection = self._get_collection()
        if collection is None:
            return

        try:
            collection.delete(where={"file_id": file_id})
        except Exception as e:
            logger.error(f"删除索引失败: {str(e)}")

    def get_stats(self) -> Dict:
        """获取索引统计信息"""
        collection = self._get_collection()
        if collection is None:
            return {'total_chunks': 0, 'status': 'unavailable'}

        try:
            count = collection.count()
            return {'total_chunks': count, 'status': 'active'}
        except Exception as e:
            return {'total_chunks': 0, 'status': 'error', 'error': str(e)}
