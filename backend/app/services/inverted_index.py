"""关键词倒排索引与结构化标签索引服务"""
import os
import json
import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
import jieba

logger = logging.getLogger(__name__)


class InvertedIndex:
    """关键词倒排索引 - 支持精确匹配与多维过滤"""

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'inverted_index'
        )
        # 倒排索引: keyword -> {doc_id: [positions]}
        self.index: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        # 文档长度（用于TF-IDF计算）
        self.doc_lengths: Dict[str, int] = {}
        # 文档总数
        self.total_docs: int = 0
        # 停用词
        self.stop_words = self._load_stop_words()
        # 军标关键词权重
        self.military_keywords = self._load_military_keywords()

        self._load()

    def index_document(self, doc_id: str, text: str, tags: Dict = None):
        """对文档建立倒排索引"""
        # 分词
        tokens = self._tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)
        self.total_docs += 1

        # 建立倒排索引
        for pos, token in enumerate(tokens):
            if token not in self.stop_words and len(token) > 1:
                self.index[token][doc_id].append(pos)

        # 建立标签索引
        if tags:
            for tag_key, tag_value in tags.items():
                tag_token = f"__tag__{tag_key}:{tag_value}"
                self.index[tag_token][doc_id].append(0)

        self._save()

    def search(self, query: str, top_k: int = 10, filters: Dict = None,
               use_military_boost: bool = True) -> List[Dict]:
        """关键词搜索，支持多维过滤"""
        query_tokens = self._tokenize(query)

        # 计算每个文档的得分
        scores: Dict[str, float] = defaultdict(float)

        for token in query_tokens:
            if token in self.index:
                # TF-IDF得分
                idf = self._compute_idf(token)
                for doc_id, positions in self.index[token].items():
                    tf = len(positions) / max(self.doc_lengths.get(doc_id, 1), 1)
                    scores[doc_id] += tf * idf

                    # 军标关键词加权
                    if use_military_boost and token in self.military_keywords:
                        scores[doc_id] *= self.military_keywords[token]

        # 应用过滤条件
        if filters:
            scores = self._apply_filters(scores, filters)

        # 排序返回
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [{'doc_id': doc_id, 'score': score} for doc_id, score in sorted_results]

    def search_by_tags(self, tags: Dict, top_k: int = 10) -> List[Dict]:
        """按标签精确搜索"""
        scores: Dict[str, float] = defaultdict(float)

        for tag_key, tag_value in tags.items():
            tag_token = f"__tag__{tag_key}:{tag_value}"
            if tag_token in self.index:
                for doc_id in self.index[tag_token]:
                    scores[doc_id] += 1.0

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{'doc_id': doc_id, 'score': score} for doc_id, score in sorted_results]

    def multi_field_search(self, query: str, fields: Dict[str, float],
                           top_k: int = 10) -> List[Dict]:
        """多字段加权搜索"""
        scores: Dict[str, float] = defaultdict(float)

        for field_name, weight in fields.items():
            field_query = query
            field_tag = f"__field__{field_name}"
            query_tokens = self._tokenize(field_query)

            for token in query_tokens:
                if token in self.index:
                    idf = self._compute_idf(token)
                    for doc_id, positions in self.index[token].items():
                        tf = len(positions) / max(self.doc_lengths.get(doc_id, 1), 1)
                        scores[doc_id] += (tf * idf * weight)

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{'doc_id': doc_id, 'score': score} for doc_id, score in sorted_results]

    def delete_document(self, doc_id: str):
        """删除文档索引"""
        if doc_id in self.doc_lengths:
            del self.doc_lengths[doc_id]
            self.total_docs -= 1

        # 从倒排索引中移除
        for keyword in list(self.index.keys()):
            if doc_id in self.index[keyword]:
                del self.index[keyword][doc_id]
            if not self.index[keyword]:
                del self.index[keyword]

        self._save()

    def _tokenize(self, text: str) -> List[str]:
        """中文分词"""
        # 使用jieba分词
        tokens = list(jieba.cut(text))
        # 过滤空白和标点
        tokens = [t.strip() for t in tokens if t.strip() and len(t.strip()) > 0]
        return tokens

    def _compute_idf(self, token: str) -> float:
        """计算IDF"""
        doc_freq = len(self.index.get(token, {}))
        if doc_freq == 0:
            return 0
        import math
        return math.log((self.total_docs + 1) / (doc_freq + 1)) + 1

    def _apply_filters(self, scores: Dict[str, float], filters: Dict) -> Dict[str, float]:
        """应用过滤条件"""
        filtered = {}
        for doc_id, score in scores.items():
            match = True
            for filter_key, filter_value in filters.items():
                tag_token = f"__tag__{filter_key}:{filter_value}"
                if tag_token not in self.index or doc_id not in self.index[tag_token]:
                    match = False
                    break
            if match:
                filtered[doc_id] = score
        return filtered

    def _load_stop_words(self) -> Set[str]:
        """加载停用词"""
        return {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
                '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你',
                '会', '着', '没有', '看', '好', '自己', '这', '他', '她', '它'}

    def _load_military_keywords(self) -> Dict[str, float]:
        """加载军标关键词及权重"""
        return {
            '需求': 1.5, '规格': 1.5, '设计': 1.5, '测试': 1.5, '接口': 1.8,
            '配置': 1.5, '版本': 1.3, '安全': 1.8, '可靠性': 1.8, '维护': 1.3,
            '功能': 1.5, '性能': 1.5, '数据': 1.3, '算法': 1.5, '流程': 1.3,
            '输入': 1.3, '输出': 1.3, '约束': 1.5, '验证': 1.5, '确认': 1.5,
            '军标': 2.0, 'GJB': 2.0, '438C': 2.0, '438B': 2.0,
            '软件需求': 1.8, '软件设计': 1.8, '软件测试': 1.8,
            '体系结构': 1.8, '详细设计': 1.8, '概要设计': 1.8,
        }

    def _save(self):
        """持久化索引"""
        os.makedirs(self.storage_path, exist_ok=True)
        data = {
            'index': dict(self.index),
            'doc_lengths': self.doc_lengths,
            'total_docs': self.total_docs
        }
        filepath = os.path.join(self.storage_path, 'inverted_index.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def _load(self):
        """加载已有索引"""
        filepath = os.path.join(self.storage_path, 'inverted_index.json')
        if not os.path.exists(filepath):
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.index = defaultdict(lambda: defaultdict(list))
            for k, v in data.get('index', {}).items():
                self.index[k] = defaultdict(list, v)
            self.doc_lengths = data.get('doc_lengths', {})
            self.total_docs = data.get('total_docs', 0)
        except Exception as e:
            logger.error(f"倒排索引加载失败: {str(e)}")

    def get_stats(self) -> Dict:
        """获取索引统计"""
        return {
            'total_docs': self.total_docs,
            'total_keywords': len(self.index),
            'total_relations': sum(len(v) for v in self.index.values())
        }
