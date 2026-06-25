"""Rerank重排序服务 - 结合军标关键词和知识图谱实体关系精准打分过滤"""
import os
import json
import logging
import math
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class RerankService:
    """Rerank服务 - 对召回结果进行精准重排序"""

    # 军标领域关键术语
    MILITARY_DOMAIN_TERMS = {
        '需求分析', '概要设计', '详细设计', '接口设计', '数据库设计',
        '软件需求', '软件设计', '软件测试', '配置管理', '质量保证',
        '功能需求', '性能需求', '接口需求', '数据需求', '安全需求',
        '体系结构', '模块设计', '算法设计', '数据结构', '状态转换',
        '测试用例', '测试规程', '测试报告', '验收测试', '回归测试',
        'GJB', '438C', '438B', '军标', '军用', '武器', '装备',
        '可靠性', '安全性', '保密性', '可用性', '维护性',
    }

    # 军标关键词权重
    MILITARY_KEYWORD_WEIGHTS = {
        'GJB': 3.0, '438C': 3.0, '438B': 3.0, '军标': 2.5, '军用': 2.0,
        '需求': 1.8, '设计': 1.8, '测试': 1.8, '接口': 2.0, '配置': 1.5,
        '安全': 2.0, '可靠': 2.0, '功能': 1.5, '性能': 1.5, '数据': 1.3,
        '验证': 1.8, '确认': 1.8, '评审': 1.5, '审计': 1.5,
    }

    def __init__(self, knowledge_graph=None, inverted_index=None):
        self.knowledge_graph = knowledge_graph
        self.inverted_index = inverted_index

    def rerank(self, query: str, candidates: List[Dict], top_k: int = 5,
               use_kg_boost: bool = True, use_military_boost: bool = True) -> List[Dict]:
        """对召回结果进行重排序

        Args:
            query: 查询文本
            candidates: 候选结果列表，每项包含 content, metadata, score 等
            top_k: 返回top-k结果
            use_kg_boost: 是否使用知识图谱增强
            use_military_boost: 是否使用军标关键词加权
        """
        if not candidates:
            return []

        scored_candidates = []
        for candidate in candidates:
            score = candidate.get('score', candidate.get('distance', 0))

            # 1. 语义相似度归一化
            semantic_score = self._normalize_semantic_score(score)

            # 2. 军标关键词匹配度
            military_score = 0
            if use_military_boost:
                military_score = self._compute_military_score(query, candidate)

            # 3. 知识图谱关联度
            kg_score = 0
            if use_kg_boost and self.knowledge_graph:
                kg_score = self._compute_kg_score(query, candidate)

            # 4. 结构化元数据匹配度
            metadata_score = self._compute_metadata_score(query, candidate)

            # 5. 内容质量分
            quality_score = self._compute_quality_score(candidate)

            # 综合得分
            final_score = (
                semantic_score * 0.3 +
                military_score * 0.25 +
                kg_score * 0.2 +
                metadata_score * 0.15 +
                quality_score * 0.1
            )

            scored_candidates.append({
                **candidate,
                'rerank_score': final_score,
                'score_details': {
                    'semantic': round(semantic_score, 4),
                    'military': round(military_score, 4),
                    'kg': round(kg_score, 4),
                    'metadata': round(metadata_score, 4),
                    'quality': round(quality_score, 4)
                }
            })

        # 排序
        scored_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)

        return scored_candidates[:top_k]

    def _normalize_semantic_score(self, score: float) -> float:
        """归一化语义相似度得分"""
        if score < 0:
            # 距离型得分（越小越好），转换为相似度
            return 1.0 / (1.0 + score)
        elif score > 1:
            return min(score / 2.0, 1.0)
        else:
            return score

    def _compute_military_score(self, query: str, candidate: Dict) -> float:
        """计算军标关键词匹配度"""
        content = candidate.get('content', '')
        combined_text = f"{query} {content}"

        score = 0.0
        matched_keywords = 0

        for keyword, weight in self.MILITARY_KEYWORD_WEIGHTS.items():
            if keyword in combined_text:
                # 查询和内容都包含该关键词，高分
                if keyword in query and keyword in content:
                    score += weight * 2.0
                # 仅内容包含
                elif keyword in content:
                    score += weight * 0.5
                matched_keywords += 1

        # 归一化
        if matched_keywords > 0:
            score = score / (matched_keywords * 3.0)  # 最大权重3.0

        return min(score, 1.0)

    def _compute_kg_score(self, query: str, candidate: Dict) -> float:
        """计算知识图谱关联度"""
        if not self.knowledge_graph:
            return 0

        score = 0.0
        metadata = candidate.get('metadata', {})

        # 检查查询中的实体是否在知识图谱中
        query_entities = self.knowledge_graph.find_entities_by_name(query)
        if query_entities:
            score += 0.3

        # 检查元数据中的章节是否与知识图谱关联
        chapter_number = metadata.get('chapter_number', '')
        if chapter_number:
            chapter_entities = self.knowledge_graph.find_entities_by_type('chapter')
            for ch in chapter_entities:
                if ch.get('properties', {}).get('number', '').startswith(chapter_number):
                    score += 0.4
                    # 检查是否有关联的代码实体
                    relations = self.knowledge_graph.get_relations(ch['id'], 'incoming')
                    code_relations = [r for r in relations if r['relation'] == 'maps_to_chapter']
                    if code_relations:
                        score += 0.3
                    break

        # 检查术语关联
        doc_type = metadata.get('doc_type', '')
        if doc_type:
            doc_entities = self.knowledge_graph.find_entities_by_name(doc_type)
            if doc_entities:
                score += 0.2

        return min(score, 1.0)

    def _compute_metadata_score(self, query: str, candidate: Dict) -> float:
        """计算元数据匹配度"""
        metadata = candidate.get('metadata', {})
        score = 0.0

        # 章节匹配
        query_lower = query.lower()
        chapter_title = metadata.get('chapter_title', '')
        if chapter_title and any(word in chapter_title for word in query_lower.split()):
            score += 0.4

        # 文档类型匹配
        doc_type = metadata.get('doc_type', '')
        if doc_type and doc_type in query:
            score += 0.3

        # 父级章节上下文匹配
        parent_chapters = metadata.get('parent_chapters', [])
        if parent_chapters:
            for parent in parent_chapters:
                if any(word in parent for word in query_lower.split()):
                    score += 0.15
                    break

        # 实体类型匹配
        entity_type = metadata.get('entity_type', '')
        if entity_type and entity_type in query:
            score += 0.15

        return min(score, 1.0)

    def _compute_quality_score(self, candidate: Dict) -> float:
        """计算内容质量分"""
        content = candidate.get('content', '')
        if not content:
            return 0

        score = 0.5  # 基础分

        # 内容长度适中
        length = len(content)
        if 50 <= length <= 2000:
            score += 0.2
        elif length > 2000:
            score += 0.1

        # 包含结构化要素
        if any(marker in content for marker in ['[章节]', '[段落]', '[要素-', '[函数]', '[类]']):
            score += 0.15

        # 包含军标术语
        domain_term_count = sum(1 for term in self.MILITARY_DOMAIN_TERMS if term in content)
        score += min(domain_term_count * 0.03, 0.15)

        return min(score, 1.0)

    def rerank_with_source_trace(self, query: str, candidates: List[Dict],
                                  top_k: int = 5) -> List[Dict]:
        """带溯源定位的重排序"""
        reranked = self.rerank(query, candidates, top_k)

        # 为每个结果添加溯源信息
        for result in reranked:
            result['source_trace'] = self._build_source_trace(result)

        return reranked

    def _build_source_trace(self, result: Dict) -> Dict:
        """构建答案溯源定位信息"""
        metadata = result.get('metadata', {})

        trace = {
            'source_type': metadata.get('chunk_type', 'unknown'),
            'source_file': metadata.get('filename', metadata.get('original_filename', '')),
            'source_file_id': metadata.get('file_id', ''),
            'chapter_number': metadata.get('chapter_number', ''),
            'chapter_title': metadata.get('chapter_title', ''),
            'parent_context': metadata.get('parent_chapters', []),
            'entity_name': metadata.get('entity_name', ''),
            'entity_type': metadata.get('entity_type', ''),
            'start_line': metadata.get('start_line', 0),
            'end_line': metadata.get('end_line', 0),
            'confidence': round(result.get('rerank_score', 0), 4),
        }

        return trace
