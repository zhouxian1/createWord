"""知识图谱服务 - 构建438C领域知识图谱，建立代码实体与文档要素映射"""
import os
import json
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """438C领域知识图谱服务 - 构建"文档-章节-要素-术语"实体与关系"""

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'knowledge_graph'
        )
        # 实体存储: {entity_id: {type, name, properties}}
        self.entities: Dict[str, Dict] = {}
        # 关系存储: [(source_id, relation_type, target_id, properties)]
        self.relations: List[Tuple] = []
        # 索引
        self._name_index: Dict[str, Set[str]] = defaultdict(set)  # name -> entity_ids
        self._type_index: Dict[str, Set[str]] = defaultdict(set)  # type -> entity_ids
        self._relation_index: Dict[str, List[int]] = defaultdict(list)  # entity_id -> relation_indices
        self._relation_keys: Set[Tuple[str, str, str]] = set()

        # 加载已有数据
        self._load()

    def add_entity(self, entity_type: str, name: str, properties: Dict = None) -> str:
        """添加实体"""
        entity_id = f"{entity_type}_{name}_{hash(name) % 10000}"
        self.entities[entity_id] = {
            'type': entity_type,
            'name': name,
            'properties': properties or {}
        }
        self._name_index[name].add(entity_id)
        self._type_index[entity_type].add(entity_id)
        return entity_id

    def add_relation(self, source_id: str, relation_type: str, target_id: str, properties: Dict = None):
        """添加关系"""
        relation_key = (source_id, relation_type, target_id)
        if relation_key in self._relation_keys:
            return
        idx = len(self.relations)
        self.relations.append((source_id, relation_type, target_id, properties or {}))
        self._relation_index[source_id].append(idx)
        self._relation_index[target_id].append(idx)
        self._relation_keys.add(relation_key)

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """获取实体"""
        return self.entities.get(entity_id)

    def find_entities_by_name(self, name: str) -> List[Dict]:
        """按名称查找实体"""
        entity_ids = self._name_index.get(name, set())
        return [{'id': eid, **self.entities[eid]} for eid in entity_ids if eid in self.entities]

    def find_entities_by_type(self, entity_type: str) -> List[Dict]:
        """按类型查找实体"""
        entity_ids = self._type_index.get(entity_type, set())
        return [{'id': eid, **self.entities[eid]} for eid in entity_ids if eid in self.entities]

    def get_relations(self, entity_id: str, direction: str = 'both') -> List[Dict]:
        """获取实体的关系"""
        results = []
        for idx in self._relation_index.get(entity_id, []):
            source_id, rel_type, target_id, props = self.relations[idx]
            if direction == 'outgoing' and source_id != entity_id:
                continue
            if direction == 'incoming' and target_id != entity_id:
                continue
            results.append({
                'source': source_id,
                'relation': rel_type,
                'target': target_id,
                'properties': props
            })
        return results

    def build_438c_graph(self, standard_docs: Dict):
        """从438C标准文档定义构建知识图谱"""
        for doc_code, doc_config in standard_docs.items():
            # 添加文档实体
            doc_id = self.add_entity('document', doc_config.get('name', doc_code), {
                'code': doc_code,
                'category': doc_config.get('category', ''),
                'complexity': doc_config.get('complexity', ''),
                'description': doc_config.get('description', '')
            })

            # 添加章节实体和关系
            for chapter in doc_config.get('chapters', []):
                ch_id = self.add_entity('chapter', chapter.get('title', ''), {
                    'number': chapter.get('number', ''),
                    'level': chapter.get('level', 1),
                    'doc_code': doc_code
                })
                self.add_relation(doc_id, 'contains_chapter', ch_id)

                # 递归处理子章节
                for sub_ch in chapter.get('sub_chapters', []):
                    sub_id = self.add_entity('chapter', sub_ch.get('title', ''), {
                        'number': sub_ch.get('number', ''),
                        'level': sub_ch.get('level', 2),
                        'doc_code': doc_code
                    })
                    self.add_relation(ch_id, 'contains_subchapter', sub_id)
                    self.add_relation(doc_id, 'contains_chapter', sub_id)

        self._save()
        logger.info(f"438C知识图谱构建完成: {len(self.entities)}个实体, {len(self.relations)}条关系")

    def ensure_438c_graph(self, standard_docs: Dict):
        """确保438C标准图谱已初始化。"""
        if self.find_entities_by_type('document'):
            return
        self.build_438c_graph(standard_docs)

    def build_code_mapping(self, code_entities: List[Dict], doc_type: str):
        """建立代码实体与438C文档要素的映射关系"""
        # 代码实体类型到438C章节的映射规则
        mapping_rules = {
            'class': {
                'SRS': '3.2',   # 软件需求规格说明 - 功能需求
                'SDD': '4.1',   # 软件设计说明 - 体系结构设计
                'SCD': '3.1',   # 软件配置项测试说明 - 测试项
            },
            'interface': {
                'SRS': '3.3',   # 接口需求
                'SDD': '4.3',   # 接口设计
                'IDD': '4.1',   # 接口设计说明
            },
            'function': {
                'SRS': '3.2',   # 功能需求
                'SDD': '4.2',   # 详细设计
                'STD': '4.2',   # 测试说明
            },
            'method': {
                'SRS': '3.2',
                'SDD': '4.2',
            },
            'variable': {
                'SDD': '4.4',   # 数据设计
            },
            'constant': {
                'SDD': '4.4',
            }
        }

        for code_entity in code_entities:
            entity_type = code_entity.get('entity_type', '')
            entity_name = code_entity.get('name', '')
            language = code_entity.get('language', '')

            # 添加代码实体
            code_id = self.add_entity('code_entity', entity_name, {
                'type': entity_type,
                'language': language,
                'filename': code_entity.get('filename', ''),
                'start_line': code_entity.get('start_line', 0),
                'end_line': code_entity.get('end_line', 0),
                'docstring': code_entity.get('docstring', ''),
                'parameters': code_entity.get('parameters', []),
                'return_type': code_entity.get('return_type', ''),
                'modifiers': code_entity.get('modifiers', []),
            })

            # 建立映射关系
            rules = mapping_rules.get(entity_type, {})
            if doc_type in rules:
                chapter_number = rules[doc_type]
                # 查找对应的章节实体
                chapter_entities = self.find_entities_by_type('chapter')
                for ch in chapter_entities:
                    if ch.get('properties', {}).get('number', '').startswith(chapter_number):
                        self.add_relation(code_id, 'maps_to_chapter', ch['id'], {
                            'doc_type': doc_type,
                            'mapping_type': 'auto',
                            'confidence': 0.8
                        })
                        break

        self._save()
        logger.info(f"代码映射构建完成: {len(code_entities)}个代码实体已映射")

    def add_term(self, term: str, definition: str = '', category: str = ''):
        """添加术语实体"""
        term_id = self.add_entity('term', term, {
            'definition': definition,
            'category': category
        })
        return term_id

    def link_term_to_chapter(self, term_name: str, chapter_number: str, doc_code: str):
        """关联术语到章节"""
        term_entities = self.find_entities_by_name(term_name)
        chapter_entities = self.find_entities_by_type('chapter')

        for term in term_entities:
            for ch in chapter_entities:
                if (ch.get('properties', {}).get('number', '').startswith(chapter_number) and
                        ch.get('properties', {}).get('doc_code', '') == doc_code):
                    self.add_relation(term['id'], 'used_in_chapter', ch['id'])

    def search_related(self, entity_name: str, depth: int = 2) -> Dict:
        """搜索相关实体（支持多跳查询）"""
        results = {'entities': [], 'relations': []}
        visited = set()

        # 查找起始实体
        start_entities = self.find_entities_by_name(entity_name)
        if not start_entities:
            return results

        # BFS遍历
        queue = [(e['id'], 0) for e in start_entities]
        while queue:
            current_id, current_depth = queue.pop(0)
            if current_id in visited or current_depth > depth:
                continue
            visited.add(current_id)

            entity = self.get_entity(current_id)
            if entity:
                results['entities'].append({'id': current_id, **entity})

            for rel in self.get_relations(current_id):
                results['relations'].append(rel)
                other_id = rel['target'] if rel['source'] == current_id else rel['source']
                if other_id not in visited:
                    queue.append((other_id, current_depth + 1))

        return results

    def get_code_chapter_mapping(self, doc_type: str) -> List[Dict]:
        """获取代码实体到文档章节的映射关系"""
        mappings = []
        code_entities = self.find_entities_by_type('code_entity')

        for code in code_entities:
            relations = self.get_relations(code['id'], 'outgoing')
            for rel in relations:
                if rel['relation'] == 'maps_to_chapter':
                    target = self.get_entity(rel['target'])
                    if target:
                        mappings.append({
                            'code_entity': code['name'],
                            'code_type': code['properties'].get('type', ''),
                            'chapter_number': target['properties'].get('number', ''),
                            'chapter_title': target['name'],
                            'doc_type': doc_type,
                            'confidence': rel['properties'].get('confidence', 0)
                        })

        return mappings

    def export_graph(self) -> Dict:
        """导出完整知识图谱"""
        return {
            'entities': {eid: data for eid, data in self.entities.items()},
            'relations': [
                {'source': r[0], 'type': r[1], 'target': r[2], 'properties': r[3]}
                for r in self.relations
            ],
            'stats': {
                'total_entities': len(self.entities),
                'total_relations': len(self.relations),
                'entity_types': dict((k, len(v)) for k, v in self._type_index.items())
            }
        }

    def _save(self):
        """持久化知识图谱"""
        os.makedirs(self.storage_path, exist_ok=True)
        data = self.export_graph()
        filepath = os.path.join(self.storage_path, 'knowledge_graph.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self):
        """加载已有知识图谱"""
        filepath = os.path.join(self.storage_path, 'knowledge_graph.json')
        if not os.path.exists(filepath):
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.entities = data.get('entities', {})
            self.relations = [
                (r['source'], r['type'], r['target'], r.get('properties', {}))
                for r in data.get('relations', [])
            ]

            # 重建索引
            self._name_index.clear()
            self._type_index.clear()
            self._relation_index.clear()
            self._relation_keys.clear()

            for eid, entity in self.entities.items():
                self._name_index[entity.get('name', '')].add(eid)
                self._type_index[entity.get('type', '')].add(eid)

            for idx, (source, rel_type, target, props) in enumerate(self.relations):
                self._relation_index[source].append(idx)
                self._relation_index[target].append(idx)
                self._relation_keys.add((source, rel_type, target))

            logger.info(f"知识图谱加载完成: {len(self.entities)}个实体, {len(self.relations)}条关系")
        except Exception as e:
            logger.error(f"知识图谱加载失败: {str(e)}")
