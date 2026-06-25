"""438C文档生成服务"""
import os
import json
import tempfile
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app import db
from app.models.models import Document, DocumentChapter, GenerationTask, Project
from app.services.llm_service import LLMService
from app.services.semantic_indexer import SemanticIndexer
from app.config.standard_documents import STANDARD_438C_DOCUMENTS

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """438C文档生成器"""

    def __init__(self, llm_service: LLMService = None, indexer: SemanticIndexer = None):
        self.llm = llm_service or LLMService()
        self.indexer = indexer or SemanticIndexer()

    def create_document(self, project_id: int, doc_type: str, generation_mode: str = 'full') -> Document:
        """创建438C文档框架"""
        doc_config = STANDARD_438C_DOCUMENTS.get(doc_type)
        if not doc_config:
            raise ValueError(f"不支持的文档类型: {doc_type}")

        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")

        # 创建文档记录
        document = Document(
            project_id=project_id,
            doc_type=doc_type,
            doc_name=doc_config['name'],
            doc_code=doc_config['code'],
            status='draft',
            generation_mode=generation_mode
        )
        db.session.add(document)
        db.session.flush()

        # 创建章节结构
        self._create_chapters(document.id, doc_config['chapters'])
        db.session.commit()

        return document

    def _create_chapters(self, document_id: int, chapters: List[Dict], parent_id: int = None,
                         sort_order: int = 0):
        """递归创建章节结构"""
        for i, ch in enumerate(chapters):
            chapter = DocumentChapter(
                document_id=document_id,
                chapter_number=ch['number'],
                chapter_title=ch['title'],
                chapter_level=ch['level'],
                generation_status='pending',
                validation_status='pending',
                sort_order=sort_order + i,
                parent_id=parent_id
            )
            db.session.add(chapter)
            db.session.flush()

            # 递归创建子章节
            if ch.get('sub_chapters'):
                self._create_chapters(document_id, ch['sub_chapters'], chapter.id,
                                      sort_order * 100 + i * 10)

    def generate_full(self, document_id: int, project_info: Dict = None) -> GenerationTask:
        """一键生成完整文档"""
        document = Document.query.get(document_id)
        if not document:
            raise ValueError(f"文档不存在: {document_id}")

        task = GenerationTask(
            document_id=document_id,
            task_type='full',
            status='running',
            started_at=datetime.utcnow()
        )
        db.session.add(task)
        document.status = 'generating'
        db.session.commit()

        try:
            chapters = DocumentChapter.query.filter_by(document_id=document_id)\
                .order_by(DocumentChapter.sort_order).all()

            total = len(chapters)
            for i, chapter in enumerate(chapters):
                self._generate_chapter_content(chapter, document, project_info)
                task.progress = int((i + 1) / total * 100)
                db.session.commit()

            document.status = 'generated'
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
        except Exception as e:
            document.status = 'error'
            task.status = 'failed'
            task.error_message = str(e)
            logger.error(f"文档生成失败: {str(e)}")
        finally:
            db.session.commit()

        return task

    def generate_by_chapter(self, document_id: int, chapter_ids: List[int],
                            project_info: Dict = None) -> GenerationTask:
        """按章节生成文档"""
        document = Document.query.get(document_id)
        if not document:
            raise ValueError(f"文档不存在: {document_id}")

        task = GenerationTask(
            document_id=document_id,
            task_type='chapter',
            target_chapters=json.dumps(chapter_ids),
            status='running',
            started_at=datetime.utcnow()
        )
        db.session.add(task)
        db.session.commit()

        try:
            chapters = DocumentChapter.query.filter(
                DocumentChapter.id.in_(chapter_ids),
                DocumentChapter.document_id == document_id
            ).order_by(DocumentChapter.sort_order).all()

            total = len(chapters)
            for i, chapter in enumerate(chapters):
                self._generate_chapter_content(chapter, document, project_info)
                task.progress = int((i + 1) / total * 100)
                db.session.commit()

            task.status = 'completed'
            task.completed_at = datetime.utcnow()
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
        finally:
            db.session.commit()

        return task

    def generate_from_code(self, project_id: int, doc_type: str,
                           code_files: List[str], project_info: Dict = None) -> Document:
        """从代码生成文档（支持MinIO存储路径）"""
        from app.services.storage_service import get_storage
        storage = get_storage()

        # 收集代码内容
        code_contents = []
        for file_path in code_files:
            try:
                if not os.path.isabs(file_path):
                    # MinIO对象名，下载到临时文件
                    ext = os.path.splitext(file_path)[1] or '.txt'
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode='w') as tmp:
                        tmp_path = tmp.name
                    if storage.download_file(file_path, tmp_path):
                        with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                            code_contents.append({
                                'file': os.path.basename(file_path),
                                'content': f.read()
                            })
                        os.unlink(tmp_path)
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code_contents.append({
                            'file': os.path.basename(file_path),
                            'content': f.read()
                        })
            except Exception as e:
                logger.warning(f"读取代码文件失败: {file_path}, {str(e)}")

        if not code_contents:
            raise ValueError("没有可用的代码文件")

        # 创建文档
        document = self.create_document(project_id, doc_type, 'code')

        # 从代码生成各章节内容
        combined_code = '\n\n'.join([
            f"// 文件: {c['file']}\n{c['content']}" for c in code_contents
        ])

        language = self._detect_language(code_files)
        result = self.llm.generate_from_code(combined_code, language, doc_type, project_info)

        # 将生成的内容分配到各章节
        chapters = DocumentChapter.query.filter_by(document_id=document.id)\
            .order_by(DocumentChapter.sort_order).all()

        if result['status'] in ('success', 'mock') and chapters:
            # 简单地将生成内容分配到第一个主章节
            for chapter in chapters:
                if chapter.chapter_level == 1:
                    chapter.content = result['content']
                    chapter.generation_status = 'completed'
                    break

        document.status = 'generated'
        db.session.commit()

        return document

    def _generate_chapter_content(self, chapter: DocumentChapter, document: Document,
                                  project_info: Dict = None):
        """生成单个章节内容"""
        # 获取知识库上下文
        context = self._get_context(chapter, document)

        # 调用LLM生成
        result = self.llm.generate_chapter(
            doc_type=document.doc_type,
            chapter_number=chapter.chapter_number,
            chapter_title=chapter.chapter_title,
            context=context,
            project_info=project_info
        )

        if result['status'] in ('success', 'mock'):
            chapter.content = result['content']
            chapter.generation_status = 'completed'
        else:
            chapter.generation_status = 'error'
            logger.error(f"章节生成失败: {chapter.chapter_number} {chapter.chapter_title}")

    def _get_context(self, chapter: DocumentChapter, document: Document) -> str:
        """从知识库获取相关上下文"""
        query = f"{document.doc_name} {chapter.chapter_title} {chapter.chapter_number}"
        results = self.indexer.search(query, n_results=3)

        if results:
            return '\n\n'.join([r['content'] for r in results])
        return ''

    def _detect_language(self, file_paths: List[str]) -> str:
        """检测代码语言"""
        ext_map = {
            '.py': 'Python', '.java': 'Java', '.c': 'C', '.h': 'C',
            '.cpp': 'C++', '.hpp': 'C++', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.js': 'JavaScript', '.ts': 'TypeScript'
        }
        for fp in file_paths:
            ext = os.path.splitext(fp)[1].lower()
            if ext in ext_map:
                return ext_map[ext]
        return 'Unknown'
