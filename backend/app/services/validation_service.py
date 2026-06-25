"""438C质量验证服务"""
import json
import re
import logging
from typing import Dict, List, Tuple
from datetime import datetime

from app import db
from app.models.models import Document, DocumentChapter, ValidationRule
from app.config.validation_rules import VALIDATION_RULES, VALIDATION_WEIGHTS, VALIDATION_LEVELS
from app.config.standard_documents import STANDARD_438C_DOCUMENTS

logger = logging.getLogger(__name__)


class ValidationService:
    """438C质量验证服务 - 对章节完整性、要素合规性进行自动校验"""

    def validate_document(self, document_id: int) -> Dict:
        """验证文档"""
        document = Document.query.get(document_id)
        if not document:
            raise ValueError(f"文档不存在: {document_id}")

        chapters = DocumentChapter.query.filter_by(document_id=document_id).all()
        chapter_map = {ch.chapter_number: ch for ch in chapters}

        # 获取验证规则
        rules = self._get_rules(document.doc_type)

        # 执行验证
        results = []
        for rule in rules:
            result = self._check_rule(rule, chapter_map, document)
            results.append(result)

        # 计算评分
        score = self._calculate_score(results)

        # 保存验证结果
        document.validation_result = json.dumps(results, ensure_ascii=False)
        document.validation_score = score
        db.session.commit()

        # 确定验证等级
        level = self._get_validation_level(score)

        return {
            'document_id': document_id,
            'doc_type': document.doc_type,
            'doc_name': document.doc_name,
            'score': score,
            'level': level,
            'total_rules': len(results),
            'passed': len([r for r in results if r['passed']]),
            'failed': len([r for r in results if not r['passed']]),
            'errors': len([r for r in results if not r['passed'] and r['severity'] == 'error']),
            'warnings': len([r for r in results if not r['passed'] and r['severity'] == 'warning']),
            'details': results
        }

    def _get_rules(self, doc_type: str) -> List[Dict]:
        """获取验证规则 - 通用规则 + 文档专用规则"""
        rules = []

        # 通用规则
        common_rules = VALIDATION_RULES.get('common', [])
        rules.extend(common_rules)

        # 文档专用规则
        doc_rules = VALIDATION_RULES.get(doc_type, [])
        rules.extend(doc_rules)

        # 从数据库加载自定义规则
        custom_rules = ValidationRule.query.filter_by(doc_type=doc_type, is_active=True).all()
        for rule in custom_rules:
            rules.append({
                'id': f"CUSTOM_{rule.id}",
                'name': rule.rule_name,
                'type': rule.rule_type,
                'description': rule.rule_description,
                'check': rule.check_expression,
                'severity': rule.severity
            })

        return rules

    def _check_rule(self, rule: Dict, chapter_map: Dict, document: Document) -> Dict:
        """执行单条规则校验"""
        check_expr = rule.get('check', '')
        passed = False
        message = ''

        try:
            if check_expr.startswith('chapter_exists'):
                # 检查章节是否存在
                chapter_num = self._extract_arg(check_expr)
                chapter = chapter_map.get(chapter_num)
                if chapter:
                    passed = True
                    message = f"章节 {chapter_num} 存在"
                else:
                    message = f"缺少章节 {chapter_num}"

            elif check_expr.startswith('chapter_contains'):
                # 检查章节内容包含指定关键词
                args = self._extract_args(check_expr)
                chapter_num = args[0] if args else ''
                keywords = args[1:] if len(args) > 1 else []
                chapter = chapter_map.get(chapter_num)
                if chapter and chapter.content:
                    missing = [kw for kw in keywords if kw not in chapter.content]
                    if not missing:
                        passed = True
                        message = f"章节 {chapter_num} 包含所有必需关键词"
                    else:
                        message = f"章节 {chapter_num} 缺少关键词: {', '.join(missing)}"
                else:
                    message = f"章节 {chapter_num} 无内容"

            elif check_expr.startswith('chapter_min_length'):
                args = self._extract_args(check_expr)
                chapter_num = args[0] if args else ''
                min_len = int(args[1]) if len(args) > 1 else 50
                chapter = chapter_map.get(chapter_num)
                if chapter and chapter.content and len(chapter.content) >= min_len:
                    passed = True
                    message = f"章节 {chapter_num} 内容长度达标"
                else:
                    actual_len = len(chapter.content) if chapter and chapter.content else 0
                    message = f"章节 {chapter_num} 内容不足: {actual_len}/{min_len}"

            elif check_expr.startswith('chapter_contains_numbers'):
                chapter_num = self._extract_arg(check_expr)
                chapter = chapter_map.get(chapter_num)
                if chapter and chapter.content:
                    numbers = re.findall(r'\d+\.?\d*', chapter.content)
                    if numbers:
                        passed = True
                        message = f"章节 {chapter_num} 包含量化指标"
                    else:
                        message = f"章节 {chapter_num} 缺少量化指标"
                else:
                    message = f"章节 {chapter_num} 无内容"

            elif check_expr == 'required_chapters_not_empty()':
                # 检查所有必填章节是否有内容
                doc_config = STANDARD_438C_DOCUMENTS.get(document.doc_type, {})
                empty_chapters = []
                for ch in chapter_map.values():
                    if not ch.content or not ch.content.strip():
                        empty_chapters.append(ch.chapter_number)
                if not empty_chapters:
                    passed = True
                    message = "所有必填章节均有内容"
                else:
                    message = f"以下章节内容为空: {', '.join(empty_chapters)}"

            elif check_expr == 'requirements_numbered()':
                # 检查需求是否有编号
                has_numbered = False
                for ch in chapter_map.values():
                    if ch.content and re.search(r'(?:SR|REQ)\s*[-]?\s*\d+', ch.content):
                        has_numbered = True
                        break
                passed = has_numbered
                message = "需求编号规范" if passed else "未发现标准需求编号"

            else:
                message = f"未知的校验表达式: {check_expr}"
                passed = True  # 未知规则默认通过

        except Exception as e:
            message = f"校验执行异常: {str(e)}"
            logger.error(f"规则校验异常: {rule.get('id')}, {str(e)}")

        return {
            'rule_id': rule.get('id', ''),
            'rule_name': rule.get('name', ''),
            'rule_type': rule.get('type', ''),
            'description': rule.get('description', ''),
            'severity': rule.get('severity', 'error'),
            'passed': passed,
            'message': message
        }

    def _extract_arg(self, expr: str) -> str:
        """从表达式中提取参数"""
        match = re.search(r'\(([^)]+)\)', expr)
        if match:
            return match.group(1).strip("'\"")
        return ''

    def _extract_args(self, expr: str) -> List[str]:
        """从表达式中提取多个参数"""
        match = re.search(r'\((.+)\)', expr)
        if match:
            args_str = match.group(1)
            return [a.strip().strip("'\"") for a in args_str.split(',')]
        return []

    def _calculate_score(self, results: List[Dict]) -> float:
        """计算验证评分"""
        if not results:
            return 0

        type_scores = {}
        type_counts = {}

        for result in results:
            rule_type = result['rule_type']
            if rule_type not in type_scores:
                type_scores[rule_type] = 0
                type_counts[rule_type] = 0

            type_counts[rule_type] += 1
            if result['passed']:
                # 根据严重程度给分
                if result['severity'] == 'error':
                    type_scores[rule_type] += 1.0
                elif result['severity'] == 'warning':
                    type_scores[rule_type] += 0.8
                else:
                    type_scores[rule_type] += 0.5
            else:
                if result['severity'] == 'error':
                    type_scores[rule_type] += 0
                elif result['severity'] == 'warning':
                    type_scores[rule_type] += 0.3
                else:
                    type_scores[rule_type] += 0.2

        # 计算各类型得分率
        type_rates = {}
        for t in type_scores:
            type_rates[t] = type_scores[t] / type_counts[t] if type_counts[t] > 0 else 0

        # 加权计算总分
        total_score = 0
        for t, rate in type_rates.items():
            weight = VALIDATION_WEIGHTS.get(t, 0.1)
            total_score += rate * weight

        return round(total_score * 100, 1)

    def _get_validation_level(self, score: float) -> Dict:
        """获取验证等级"""
        for level_name, level_info in VALIDATION_LEVELS.items():
            if score >= level_info['min_score']:
                return {'name': level_name, 'label': level_info['label'], 'color': level_info['color']}
        return {'name': 'unqualified', 'label': '不合格', 'color': 'red'}
