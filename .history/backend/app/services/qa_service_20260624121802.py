"""智能问答服务"""
import json
import logging
from typing import Dict, List

from app.services.llm_service import LLMService
from app.services.semantic_indexer import SemanticIndexer

logger = logging.getLogger(__name__)


class QuestionAnsweringService:
    """智能问答服务 - 基于知识库的问答"""

    def __init__(self, llm_service: LLMService = None, indexer: SemanticIndexer = None):
        self.llm = llm_service or LLMService()
        self.indexer = indexer or SemanticIndexer()

    def answer(self, question: str, knowledge_base_id: int = None,
               top_k: int = 5) -> Dict:
        """回答问题"""
        # 从知识库检索相关内容
        context_parts = []
        if knowledge_base_id:
            results = self.indexer.search(
                query=question,
                n_results=top_k,
                filter_metadata={'knowledge_base_id': knowledge_base_id}
            )
            context_parts = [r['content'] for r in results]
        else:
            results = self.indexer.search(query=question, n_results=top_k)
            context_parts = [r['content'] for r in results]

        context = '\n\n---\n\n'.join(context_parts) if context_parts else ''

        # 调用LLM生成回答
        result = self.llm.answer_question(question, context)

        return {
            'question': question,
            'answer': result.get('content', ''),
            'context_sources': len(context_parts),
            'status': result.get('status', 'unknown')
        }

    def answer_about_438c(self, question: str) -> Dict:
        """回答关于438C标准的问题"""
        from app.config.standard_documents import STANDARD_438C_DOCUMENTS, DOCUMENT_CATEGORIES

        system_prompt = """你是GJB 438C军用软件文档编制规范的专家。
请基于438C标准回答用户的问题，确保回答准确、专业。
如果问题超出438C的范围，请明确说明。"""

        # 构建438C知识上下文
        context_parts = []
        for code, doc_info in STANDARD_438C_DOCUMENTS.items():
            context_parts.append(
                f"{doc_info['name']}({code}): {doc_info['description']}"
            )

        context = '\n'.join(context_parts)

        result = self.llm.generate_with_context(system_prompt, question, context)

        return {
            'question': question,
            'answer': result.get('content', ''),
            'status': result.get('status', 'unknown')
        }
