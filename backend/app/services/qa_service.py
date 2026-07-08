"""智能问答服务 - 基于知识库语义检索与LLM生成，支持答案溯源定位"""
import json
import logging
from typing import Dict, List

from app.services.llm_service import LLMService, create_llm_service
from app.services.semantic_indexer import SemanticIndexer

logger = logging.getLogger(__name__)


class QuestionAnsweringService:
    """智能问答服务 - 基于知识库的语义检索与LLM生成，支持答案溯源定位"""

    def __init__(self, llm_service: LLMService = None, indexer: SemanticIndexer = None):
        self.llm = llm_service or create_llm_service()
        self.indexer = indexer or SemanticIndexer()

    def answer(self, question: str, knowledge_base_id: int = None,
               top_k: int = 5) -> Dict:
        """回答问题（带溯源定位）"""
        # 从知识库检索相关内容（使用Rerank+溯源）
        if knowledge_base_id:
            results = self.indexer.search_with_trace(
                query=question,
                n_results=top_k,
            )
            # 过滤指定知识库
            results = [r for r in results
                       if r.get('metadata', {}).get('knowledge_base_id') == knowledge_base_id]
        else:
            results = self.indexer.search_with_trace(query=question, n_results=top_k)

        context_parts = [r['content'] for r in results]
        context = '\n\n---\n\n'.join(context_parts) if context_parts else ''

        # 构建溯源信息
        source_traces = []
        for r in results:
            trace = r.get('source_trace', {})
            if not trace:
                # 手动构建溯源
                metadata = r.get('metadata', {})
                trace = {
                    'source_type': metadata.get('chunk_type', 'unknown'),
                    'source_file': metadata.get('original_filename', metadata.get('filename', '')),
                    'source_file_id': metadata.get('file_id', ''),
                    'chapter_number': metadata.get('chapter_number', ''),
                    'chapter_title': metadata.get('chapter_title', ''),
                    'parent_context': metadata.get('parent_chapters', []),
                    'entity_name': metadata.get('entity_name', ''),
                    'entity_type': metadata.get('entity_type', ''),
                    'confidence': round(r.get('rerank_score', r.get('score', 0)), 4),
                }
            source_traces.append(trace)

        # 调用LLM生成回答
        result = self.llm.answer_question(question, context)

        return {
            'question': question,
            'answer': result.get('content', ''),
            'context_sources': len(context_parts),
            'source_traces': source_traces,
            'status': result.get('status', 'unknown')
        }

    def answer_about_438c(self, question: str) -> Dict:
        """回答关于438C标准的问题"""
        from app.config.standard_documents import STANDARD_438C_DOCUMENTS

        system_prompt = """你是GJB 438C军用软件文档编制规范的专家。
请基于438C标准回答用户的问题，确保回答准确、专业。
如果问题超出438C的范围，请明确说明。
回答时请引用相关文档编号和章节。"""

        # 构建438C知识上下文
        context_parts = []
        question_upper = question.upper()
        matched_docs = [
            (code, doc_info)
            for code, doc_info in STANDARD_438C_DOCUMENTS.items()
            if code.upper() in question_upper or doc_info.get('name', '') in question
        ]
        if not matched_docs:
            matched_docs = list(STANDARD_438C_DOCUMENTS.items())[:8]

        for code, doc_info in matched_docs:
            chapters_desc = []
            for ch in doc_info.get('chapters', [])[:6]:
                ch_desc = f"  {ch['number']} {ch['title']}"
                if ch.get('elements'):
                    ch_desc += f" (要素: {', '.join(ch['elements'])})"
                chapters_desc.append(ch_desc)
                for sub_ch in ch.get('sub_chapters', []):
                    sub_desc = f"    {sub_ch['number']} {sub_ch['title']}"
                    if sub_ch.get('elements'):
                        sub_desc += f" (要素: {', '.join(sub_ch['elements'])})"
                    chapters_desc.append(sub_desc)

            context_parts.append(
                f"{doc_info['name']}({code}):\n"
                f"  类别: {doc_info.get('category', '')}\n"
                f"  复杂度: {doc_info.get('complexity', '')}\n"
                f"  描述: {doc_info['description']}\n"
                f"  章节结构:\n" + '\n'.join(chapters_desc)
            )

        context = '\n\n'.join(context_parts)

        user_prompt = f"参考以下438C摘要回答问题：\n---\n{context}\n---\n\n问题：{question}"
        result = self.llm.generate(system_prompt, user_prompt, temperature=0.3, max_tokens=512)

        return {
            'question': question,
            'answer': result.get('content', ''),
            'source_traces': [{
                'source_type': '438c_standard',
                'confidence': 1.0
            }],
            'status': result.get('status', 'unknown')
        }

    def answer_with_code_context(self, question: str, code_file_ids: List[int] = None) -> Dict:
        """基于代码上下文的问答"""
        # 搜索代码相关内容
        filter_meta = {}
        if code_file_ids:
            filter_meta['chunk_type'] = 'code_entity'

        results = self.indexer.search_with_trace(query=question, n_results=5)

        context_parts = [r['content'] for r in results]
        context = '\n\n---\n\n'.join(context_parts) if context_parts else ''

        system_prompt = """你是一位精通多种编程语言和GJB 438C规范的资深软件工程师。
请基于提供的代码上下文回答用户的问题。
回答时请：
1. 引用具体的代码实体（函数名、类名等）
2. 说明代码与438C文档要素的关联
3. 给出专业、准确的回答"""

        result = self.llm.generate_with_context(system_prompt, question, context)

        source_traces = []
        for r in results:
            metadata = r.get('metadata', {})
            trace = r.get('source_trace', {})
            if not trace:
                trace = {
                    'source_type': metadata.get('chunk_type', 'code'),
                    'entity_name': metadata.get('entity_name', ''),
                    'entity_type': metadata.get('entity_type', ''),
                    'language': metadata.get('language', ''),
                    'filename': metadata.get('filename', ''),
                    'confidence': round(r.get('rerank_score', r.get('score', 0)), 4),
                }
            source_traces.append(trace)

        return {
            'question': question,
            'answer': result.get('content', ''),
            'context_sources': len(context_parts),
            'source_traces': source_traces,
            'status': result.get('status', 'unknown')
        }
