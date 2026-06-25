"""语义索引服务 - 整合文档分块、向量化、倒排索引、Rerank"""
import os
import json
import logging
from typing import List, Dict, Optional

from app.services.military_doc_chunker import MilitaryDocChunker
from app.services.ast_code_parser import ASTCodeParser
from app.services.text_preprocessor import TextPreprocessor
from app.services.inverted_index import InvertedIndex
from app.services.rerank_service import RerankService
from app.services.knowledge_graph import KnowledgeGraphService
from app.config.standard_documents import STANDARD_438C_DOCUMENTS

logger = logging.getLogger(__name__)


class SemanticIndexer:
    """语义索引构建器 - 支持文档分块、向量化、倒排索引、Rerank"""

    def __init__(self, db_path=None, embedding_model=None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vector_db')
        self.embedding_model = embedding_model
        self._collection = None
        self._chroma_available = None  # None=未检测, True/False

        # 子服务
        self.chunker = MilitaryDocChunker()
        self.code_parser = ASTCodeParser()
        self.preprocessor = TextPreprocessor()
        self.inverted_index = InvertedIndex()
        self.reranker = RerankService()
        self.knowledge_graph = KnowledgeGraphService()
        self.knowledge_graph.ensure_438c_graph(STANDARD_438C_DOCUMENTS)

        # 关联知识图谱到Reranker
        self.reranker.knowledge_graph = self.knowledge_graph
        self.reranker.inverted_index = self.inverted_index

        # 纯文本索引回退（chromadb不可用时使用）
        self._text_chunks = {}  # {chunk_id: {content, metadata}}

    def _get_collection(self, collection_name='documents'):
        """获取或创建向量集合"""
        # 如果已确认不可用，直接返回
        if self._chroma_available is False:
            return None
        if self._chroma_available is True:
            try:
                import chromadb
                client = chromadb.PersistentClient(path=self.db_path)
                return client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                self._chroma_available = False
                return None
        try:
            import chromadb
            # 使用线程超时检测chromadb是否可用
            import threading
            result = [None]
            error = [None]

            def _init_chroma():
                try:
                    client = chromadb.PersistentClient(path=self.db_path)
                    result[0] = client.get_or_create_collection(
                        name=collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
                except Exception as e:
                    error[0] = e

            t = threading.Thread(target=_init_chroma, daemon=True)
            t.start()
            t.join(timeout=5)  # 5秒超时

            if t.is_alive():
                logger.warning("chromadb初始化超时(10s)，使用文本搜索回退")
                self._chroma_available = False
                return None

            if error[0]:
                raise error[0]

            self._chroma_available = True
            return result[0]
        except ImportError:
            logger.warning("chromadb未安装，语义索引功能不可用")
            self._chroma_available = False
            return None
        except Exception as e:
            logger.warning(f"chromadb初始化失败: {str(e)}，使用文本搜索回退")
            self._chroma_available = False
            return None

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
        """将文本分块（通用分块）"""
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

    def chunk_military_document(self, text: str, doc_type: str = '', metadata: Dict = None) -> List[Dict]:
        """军标文档结构化拆分 - 按"章节-段落-要素"层级"""
        return self.chunker.chunk_document(text, doc_type, metadata)

    def chunk_code_file(self, file_path: str, language: str = None) -> List[Dict]:
        """代码文件分块 - 按"函数/类/模块"粒度"""
        structure = self.code_parser.parse(file_path, language)
        return self.code_parser.get_code_chunks(structure)

    def build_index(self, file_id: int, text: str, metadata: Dict = None,
                    file_type: str = '', doc_type: str = ''):
        """为文档构建完整索引（向量+倒排+知识图谱）"""
        import sys
        # 1. 文本预处理
        logger.info(f"build_index: file_id={file_id}, text_len={len(text)}, file_type={file_type}")
        preprocess_result = self.preprocessor.preprocess(text, file_type)
        processed_text = preprocess_result['text']
        logger.info(f"build_index: 预处理完成, len={len(processed_text)}")

        # 2. 智能分块
        if file_type in ('c_code', 'cpp_code', 'python_code', 'java_code', 'dotnet_code'):
            # 代码文件：按函数/类/模块分块
            chunks = []
            # 代码分块需要文件路径，此处用通用分块
            chunks = self.chunk_text(processed_text, chunk_size=800, overlap=100)
            chunk_type = 'code'
        elif doc_type and doc_type.startswith(('SRS', 'SDD', 'STD', 'SVD', 'SCD', 'IDD', 'SSS', 'DBDD',
                                               'SPM', 'SIP', 'STR', 'SVR', 'COM', 'CPM', 'QAP', 'IRS',
                                               'ICD', 'FS', 'OCD', 'SSDD')):
            # 军标文档：结构化拆分
            chunks = self.chunk_military_document(processed_text, doc_type, metadata)
            chunk_type = 'military'
        else:
            # 通用文档：普通分块
            chunks = self.chunk_text(processed_text)
            chunk_type = 'general'

        logger.info(f"build_index: 分块完成, chunks={len(chunks)}, chunk_type={chunk_type}")

        if not chunks:
            return {'chunk_count': 0, 'status': 'empty'}

        # 3. 构建向量索引
        collection = self._get_collection()
        logger.info(f"build_index: collection获取完成, available={collection is not None}")
        try:
            ids = [f"file_{file_id}_chunk_{i}" for i in range(len(chunks))]
            documents = [chunk.get('content', chunk.get('text', '')) for chunk in chunks]
            metas = []
            for i, chunk in enumerate(chunks):
                meta = {
                    'file_id': file_id,
                    'chunk_index': i,
                    'char_count': chunk.get('char_count', len(chunk.get('content', ''))),
                    'chunk_type': chunk.get('chunk_type', chunk_type),
                }
                # 合并分块自带的元数据
                if 'metadata' in chunk:
                    meta.update(chunk['metadata'])
                if metadata:
                    meta.update(metadata)
                metas.append(meta)

            if collection is not None:
                collection.upsert(ids=ids, documents=documents, metadatas=metas)
                logger.info(f"build_index: chromadb upsert完成, {len(ids)}条")
            else:
                # chromadb不可用，存入内存文本索引
                for i, (cid, doc, meta) in enumerate(zip(ids, documents, metas)):
                    self._text_chunks[cid] = {'content': doc, 'metadata': meta}
                logger.info(f"chromadb不可用，已将{len(ids)}个分块存入内存文本索引")
        except Exception as e:
            logger.error(f"向量索引构建失败: {str(e)}")
            # 回退到内存索引
            for i, chunk in enumerate(chunks):
                cid = f"file_{file_id}_chunk_{i}"
                content = chunk.get('content', '')
                meta = {'file_id': file_id, 'chunk_index': i, 'chunk_type': chunk_type}
                if metadata:
                    meta.update(metadata)
                self._text_chunks[cid] = {'content': content, 'metadata': meta}

        # 4. 构建倒排索引
        try:
            for i, chunk in enumerate(chunks):
                content = chunk.get('content', '')
                doc_id = f"file_{file_id}_chunk_{i}"
                tags = {}
                if metadata:
                    tags.update({k: v for k, v in metadata.items() if isinstance(v, str)})
                if 'metadata' in chunk:
                    tags.update({k: v for k, v in chunk['metadata'].items() if isinstance(v, str)})
                self.inverted_index.index_document(doc_id, content, tags)
        except Exception as e:
            logger.error(f"倒排索引构建失败: {str(e)}")

        return {
            'chunk_count': len(chunks),
            'status': 'completed',
            'chunk_type': chunk_type,
            'preprocess': preprocess_result
        }

    def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None,
               use_rerank: bool = True, use_inverted: bool = True) -> List[Dict]:
        """语义搜索 - 支持向量检索+倒排检索+Rerank"""
        # 1. 向量语义检索
        vector_results = self._vector_search(query, n_results * 3, filter_metadata)

        # 如果向量搜索无结果且内存索引有数据，使用文本搜索回退
        if not vector_results and self._text_chunks:
            vector_results = self._text_search(query, n_results * 3, filter_metadata)

        # 2. 倒排索引检索
        inverted_results = []
        if use_inverted:
            try:
                inv_results = self.inverted_index.search(query, top_k=n_results * 2)
                # 转换为统一格式
                for r in inv_results:
                    doc_id = r['doc_id']
                    # 从向量库获取内容
                    parts = doc_id.split('_')
                    if len(parts) >= 4:
                        file_id = int(parts[1])
                        chunk_idx = int(parts[3])
                        collection = self._get_collection()
                        if collection:
                            try:
                                result = collection.get(ids=[doc_id], include=['documents', 'metadatas'])
                                if result['documents']:
                                    inverted_results.append({
                                        'id': doc_id,
                                        'content': result['documents'][0],
                                        'metadata': result['metadatas'][0] if result['metadatas'] else {},
                                        'score': r['score']
                                    })
                            except Exception:
                                pass
            except Exception as e:
                logger.error(f"倒排检索失败: {str(e)}")

        # 3. 合并去重
        all_results = {}
        for r in vector_results:
            all_results[r['id']] = r
        for r in inverted_results:
            if r['id'] not in all_results:
                all_results[r['id']] = r
            else:
                # 合并得分
                all_results[r['id']]['score'] = (
                    all_results[r['id']].get('score', 0) * 0.7 + r.get('score', 0) * 0.3
                )

        candidates = list(all_results.values())

        # 4. Rerank重排序
        if use_rerank and candidates:
            reranked = self.reranker.rerank_with_source_trace(query, candidates, n_results)
            return reranked

        # 不使用Rerank，直接排序返回
        candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
        return candidates[:n_results]

    def _text_search(self, query: str, n_results: int, filter_metadata: Dict = None) -> List[Dict]:
        """纯文本关键词搜索回退（chromadb不可用时使用）"""
        import jieba
        query_words = set(jieba.cut(query))
        results = []
        for chunk_id, chunk_data in self._text_chunks.items():
            # 过滤metadata
            if filter_metadata:
                meta = chunk_data.get('metadata', {})
                match = all(meta.get(k) == v for k, v in filter_metadata.items())
                if not match:
                    continue

            content = chunk_data.get('content', '')
            # 计算关键词匹配度
            content_words = set(jieba.cut(content))
            overlap = query_words & content_words
            if overlap:
                score = len(overlap) / len(query_words) if query_words else 0
                results.append({
                    'id': chunk_id,
                    'content': content,
                    'metadata': chunk_data.get('metadata', {}),
                    'score': score
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n_results]

    def _vector_search(self, query: str, n_results: int, filter_metadata: Dict = None) -> List[Dict]:
        """向量语义检索"""
        collection = self._get_collection()
        if collection is None:
            return []

        try:
            kwargs = {'query_texts': [query], 'n_results': min(n_results, collection.count() or 1)}
            if filter_metadata:
                kwargs['where'] = filter_metadata

            results = collection.query(**kwargs)

            search_results = []
            for i in range(len(results['ids'][0])):
                search_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'score': 1 - (results['distances'][0][i] if results.get('distances') else 0)
                })

            return search_results
        except Exception as e:
            logger.error(f"语义搜索失败: {str(e)}")
            return []

    def search_with_trace(self, query: str, n_results: int = 5) -> List[Dict]:
        """带溯源定位的搜索"""
        return self.search(query, n_results, use_rerank=True)

    def delete_index(self, file_id: int):
        """删除文档索引"""
        collection = self._get_collection()

        try:
            # 删除向量索引
            if collection is not None:
                all_ids = collection.get(where={"file_id": file_id})['ids']
                if all_ids:
                    collection.delete(ids=all_ids)
            else:
                # 从内存索引删除
                all_ids = [k for k in self._text_chunks if k.startswith(f"file_{file_id}_chunk_")]
                for doc_id in all_ids:
                    del self._text_chunks[doc_id]

            # 删除倒排索引
            for doc_id in all_ids:
                self.inverted_index.delete_document(doc_id)

        except Exception as e:
            logger.error(f"删除索引失败: {str(e)}")

    def get_stats(self) -> Dict:
        """获取索引统计信息"""
        collection = self._get_collection()
        vector_count = 0
        if collection:
            try:
                vector_count = collection.count()
            except Exception:
                pass

        inv_stats = self.inverted_index.get_stats()
        kg_stats = self.knowledge_graph.export_graph().get('stats', {})

        return {
            'total_chunks': vector_count,
            'vector_status': 'active' if vector_count > 0 else 'empty',
            'inverted_index': inv_stats,
            'knowledge_graph': kg_stats
        }
