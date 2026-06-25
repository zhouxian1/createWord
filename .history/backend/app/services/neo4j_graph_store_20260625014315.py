"""Neo4j graph storage adapter with graceful local fallback."""
import logging
from typing import Dict, Iterable, List


logger = logging.getLogger(__name__)


class Neo4jGraphStore:
    """Persist graph entities and relations into Neo4j when available."""

    def __init__(self, uri: str = '', user: str = '', password: str = '', database: str = 'neo4j'):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database or 'neo4j'
        self._driver = None
        self._disabled = False

    @property
    def available(self) -> bool:
        return self._get_driver() is not None

    def _get_driver(self):
        if self._disabled or not all([self.uri, self.user, self.password]):
            return None
        if self._driver is None:
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                self._driver.verify_connectivity()
            except ImportError:
                logger.warning("neo4j 驱动未安装，知识图谱回退到本地 JSON 存储")
                self._disabled = True
                return None
            except Exception as exc:
                logger.warning(f"Neo4j 不可用，知识图谱回退到本地 JSON 存储: {exc}")
                self._disabled = True
                return None
        return self._driver

    def upsert_entity(self, entity_id: str, entity: Dict):
        driver = self._get_driver()
        if driver is None:
            return

        labels = ['GraphEntity', self._normalize_label(entity.get('type', 'Unknown'))]
        properties = {
            'entity_id': entity_id,
            'name': entity.get('name', ''),
            'entity_type': entity.get('type', ''),
            'properties': entity.get('properties', {})
        }

        query = (
            f"MERGE (n:{':'.join(labels)} {{entity_id: $entity_id}}) "
            "SET n.name = $name, n.entity_type = $entity_type, n.properties = $properties"
        )
        self._run(query, properties)

    def upsert_relation(self, source_id: str, relation_type: str, target_id: str, properties: Dict):
        driver = self._get_driver()
        if driver is None:
            return

        rel_label = self._normalize_label(relation_type or 'RELATED_TO')
        query = (
            "MATCH (s:GraphEntity {entity_id: $source_id}) "
            "MATCH (t:GraphEntity {entity_id: $target_id}) "
            f"MERGE (s)-[r:{rel_label}]->(t) "
            "SET r.relation_type = $relation_type, r.properties = $properties"
        )
        self._run(query, {
            'source_id': source_id,
            'target_id': target_id,
            'relation_type': relation_type,
            'properties': properties or {}
        })

    def sync_graph(self, entities: Dict[str, Dict], relations: Iterable):
        driver = self._get_driver()
        if driver is None:
            return

        self._run("MATCH (n:GraphEntity) DETACH DELETE n", {})
        for entity_id, entity in entities.items():
            self.upsert_entity(entity_id, entity)
        for source_id, relation_type, target_id, properties in relations:
            self.upsert_relation(source_id, relation_type, target_id, properties)

    def get_stats(self) -> Dict:
        driver = self._get_driver()
        if driver is None:
            return {'enabled': False, 'connected': False}

        entity_result = self._run(
            "MATCH (n:GraphEntity) RETURN count(n) AS count",
            {},
            single=True
        )
        relation_result = self._run(
            "MATCH (:GraphEntity)-[r]->(:GraphEntity) RETURN count(r) AS count",
            {},
            single=True
        )
        return {
            'enabled': True,
            'connected': True,
            'entity_count': entity_result.get('count', 0) if entity_result else 0,
            'relation_count': relation_result.get('count', 0) if relation_result else 0,
            'database': self.database
        }

    def _run(self, query: str, parameters: Dict, single: bool = False):
        driver = self._get_driver()
        if driver is None:
            return None
        try:
            with driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                if single:
                    record = result.single()
                    return dict(record) if record else None
                return list(result)
        except Exception as exc:
            logger.warning(f"Neo4j 操作失败，已跳过当前同步: {exc}")
            self._disabled = True
            return None

    @staticmethod
    def _normalize_label(value: str) -> str:
        if not value:
            return 'Unknown'
        normalized = ''.join(ch if ch.isalnum() else '_' for ch in value)
        if normalized and normalized[0].isdigit():
            normalized = f"L_{normalized}"
        return normalized or 'Unknown'
