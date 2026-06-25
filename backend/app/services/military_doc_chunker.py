"""军标文档结构化拆分服务 - 按"章节-段落-要素"层级拆分，保留父级上下文Metadata"""
import re
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class StructuredChunk:
    """结构化分块"""
    content: str
    chunk_type: str  # chapter, paragraph, element
    chapter_number: str
    chapter_title: str
    level: int
    parent_chapters: List[str] = field(default_factory=list)  # 父级章节标题链
    metadata: Dict = field(default_factory=dict)
    elements: List[Dict] = field(default_factory=list)  # 提取的要素
    start_position: int = 0
    end_position: int = 0


class MilitaryDocChunker:
    """军标文档结构化拆分器 - 按"章节-段落-要素"层级拆分"""

    # 438C文档章节编号模式
    CHAPTER_PATTERNS = [
        # 标准编号: 1, 1.1, 1.1.1, 1.1.1.1
        re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$', re.MULTILINE),
        # 中文编号: 一、 / （一） / 1. / （1）
        re.compile(r'^([一二三四五六七八九十]+[、.])\s*(.+)$', re.MULTILINE),
        re.compile(r'^[（(]([一二三四五六七八九十]+)[）)]\s*(.+)$', re.MULTILINE),
        # 带括号编号
        re.compile(r'^(\d+(?:\.\d+)*)[）)]\s*(.+)$', re.MULTILINE),
    ]

    # 段落分隔模式
    PARAGRAPH_SEPARATOR = re.compile(r'\n\s*\n')

    # 要素提取模式
    ELEMENT_PATTERNS = {
        'table': re.compile(r'(?:表\s*\d+[\.\s]*|Table\s*\d+[\.\s]*)(.+?)(?=\n\n|\Z)', re.DOTALL),
        'figure': re.compile(r'(?:图\s*\d+[\.\s]*|Figure\s*\d+[\.\s]*)(.+?)(?=\n\n|\Z)', re.DOTALL),
        'formula': re.compile(r'[\$￥].+?[\$￥]|\\\(.+?\\\)', re.DOTALL),
        'reference': re.compile(r'\[[\d,\s]+\]|文献\s*\d+', re.MULTILINE),
        'requirement': re.compile(r'(?:应|应当|必须|需要|须|不得|禁止|不宜)\s*[，,]?\s*.+?[。；]', re.MULTILINE),
        'list_item': re.compile(r'^[a-zA-Z]\)\s*.+$|^[（(][a-zA-Z][）)]\s*.+$|^\d+[、.]\s*.+$', re.MULTILINE),
    }

    def chunk_document(self, text: str, doc_type: str = '', metadata: Dict = None) -> List[Dict]:
        """对军标文档进行结构化拆分"""
        base_metadata = metadata or {}

        # 第一步：识别章节结构
        chapters = self._extract_chapters(text)

        # 第二步：对每个章节进行段落级拆分
        chunks = []
        for chapter in chapters:
            # 构建父级章节上下文
            parent_chain = self._build_parent_chain(chapter, chapters)

            # 章节级分块
            chapter_chunk = self._create_chapter_chunk(chapter, parent_chain, base_metadata, doc_type)
            chunks.append(chapter_chunk)

            # 段落级分块
            paragraphs = self._split_paragraphs(chapter['content'])
            for para_idx, para in enumerate(paragraphs):
                # 要素级提取
                elements = self._extract_elements(para)

                para_chunk = self._create_paragraph_chunk(
                    para, chapter, parent_chain, para_idx, elements, base_metadata, doc_type
                )
                chunks.append(para_chunk)

                # 要素级分块
                for elem in elements:
                    elem_chunk = self._create_element_chunk(
                        elem, chapter, parent_chain, base_metadata, doc_type
                    )
                    chunks.append(elem_chunk)

        return chunks

    def _extract_chapters(self, text: str) -> List[Dict]:
        """识别文档中的章节结构"""
        chapters = []

        # 尝试匹配章节标题
        matches = []
        for pattern in self.CHAPTER_PATTERNS:
            for m in pattern.finditer(text):
                matches.append({
                    'number': m.group(1).strip(),
                    'title': m.group(2).strip(),
                    'start': m.start(),
                    'end': m.end()
                })

        if not matches:
            # 无章节结构，整体作为一个块
            return [{
                'number': '0',
                'title': '全文',
                'level': 0,
                'content': text,
                'start': 0,
                'end': len(text)
            }]

        # 按位置排序
        matches.sort(key=lambda x: x['start'])

        # 去重（同一位置可能被多个模式匹配）
        seen = set()
        unique_matches = []
        for m in matches:
            key = (m['number'], m['start'])
            if key not in seen:
                seen.add(key)
                unique_matches.append(m)
        matches = unique_matches

        # 计算章节层级和内容范围
        for i, match in enumerate(matches):
            level = len(match['number'].split('.'))
            content_start = match['end']
            content_end = matches[i + 1]['start'] if i + 1 < len(matches) else len(text)
            content = text[content_start:content_end].strip()

            chapters.append({
                'number': match['number'],
                'title': match['title'],
                'level': level,
                'content': content,
                'start': match['start'],
                'end': content_end
            })

        return chapters

    def _split_paragraphs(self, text: str) -> List[str]:
        """将章节内容拆分为段落"""
        paragraphs = self.PARAGRAPH_SEPARATOR.split(text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _extract_elements(self, text: str) -> List[Dict]:
        """提取段落中的要素"""
        elements = []

        for elem_type, pattern in self.ELEMENT_PATTERNS.items():
            for match in pattern.finditer(text):
                elements.append({
                    'type': elem_type,
                    'content': match.group(0).strip(),
                    'start': match.start(),
                    'end': match.end()
                })

        return elements

    def _build_parent_chain(self, chapter: Dict, all_chapters: List[Dict]) -> List[str]:
        """构建父级章节标题链作为上下文Metadata"""
        chain = []
        chapter_num = chapter['number']

        for ch in all_chapters:
            if ch['number'] == chapter_num:
                break
            # 判断是否为父级章节
            if chapter_num.startswith(ch['number'] + '.') or (
                len(ch['number'].split('.')) < len(chapter_num.split('.'))
                and self._is_ancestor(ch['number'], chapter_num)
            ):
                chain.append(f"{ch['number']} {ch['title']}")

        return chain

    def _is_ancestor(self, parent_num: str, child_num: str) -> bool:
        """判断是否为祖先章节"""
        parent_parts = parent_num.split('.')
        child_parts = child_num.split('.')
        if len(parent_parts) >= len(child_parts):
            return False
        return child_parts[:len(parent_parts)] == parent_parts

    def _create_chapter_chunk(self, chapter: Dict, parent_chain: List[str],
                               base_metadata: Dict, doc_type: str) -> Dict:
        """创建章节级分块"""
        metadata = {
            **base_metadata,
            'chunk_type': 'chapter',
            'chapter_number': chapter['number'],
            'chapter_title': chapter['title'],
            'level': chapter['level'],
            'parent_chapters': parent_chain,
            'doc_type': doc_type,
        }

        # 章节头信息
        header = ' > '.join(parent_chain + [f"{chapter['number']} {chapter['title']}"])

        return {
            'content': f"[章节] {header}\n\n{chapter['content']}",
            'metadata': metadata,
            'chunk_type': 'chapter'
        }

    def _create_paragraph_chunk(self, para: str, chapter: Dict, parent_chain: List[str],
                                 para_idx: int, elements: List[Dict],
                                 base_metadata: Dict, doc_type: str) -> Dict:
        """创建段落级分块"""
        metadata = {
            **base_metadata,
            'chunk_type': 'paragraph',
            'chapter_number': chapter['number'],
            'chapter_title': chapter['title'],
            'level': chapter['level'],
            'parent_chapters': parent_chain,
            'paragraph_index': para_idx,
            'element_count': len(elements),
            'element_types': list(set(e['type'] for e in elements)),
            'doc_type': doc_type,
        }

        header = ' > '.join(parent_chain + [f"{chapter['number']} {chapter['title']}"])

        return {
            'content': f"[段落] {header} (段落{para_idx + 1})\n\n{para}",
            'metadata': metadata,
            'chunk_type': 'paragraph'
        }

    def _create_element_chunk(self, element: Dict, chapter: Dict, parent_chain: List[str],
                               base_metadata: Dict, doc_type: str) -> Dict:
        """创建要素级分块"""
        metadata = {
            **base_metadata,
            'chunk_type': 'element',
            'element_type': element['type'],
            'chapter_number': chapter['number'],
            'chapter_title': chapter['title'],
            'parent_chapters': parent_chain,
            'doc_type': doc_type,
        }

        header = ' > '.join(parent_chain + [f"{chapter['number']} {chapter['title']}"])

        return {
            'content': f"[要素-{element['type']}] {header}\n\n{element['content']}",
            'metadata': metadata,
            'chunk_type': 'element'
        }
