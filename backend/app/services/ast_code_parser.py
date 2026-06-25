"""AST代码解析服务 - 基于抽象语法树提取函数、类、接口、注释及逻辑结构"""
import os
import ast
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class CodeEntity:
    """代码实体"""
    name: str
    entity_type: str  # class, function, method, interface, variable, constant, import
    language: str
    start_line: int
    end_line: int
    source_code: str = ''
    docstring: str = ''
    modifiers: List[str] = field(default_factory=list)  # public, private, static, etc.
    parameters: List[Dict] = field(default_factory=list)
    return_type: str = ''
    base_classes: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)  # 调用的函数/方法
    annotations: Dict = field(default_factory=dict)
    comments: List[str] = field(default_factory=list)


@dataclass
class CodeStructure:
    """代码结构"""
    filename: str
    language: str
    entities: List[CodeEntity] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    call_graph: Dict[str, List[str]] = field(default_factory=dict)  # 函数调用图
    inheritance_graph: Dict[str, List[str]] = field(default_factory=dict)  # 继承图
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0


class ASTCodeParser:
    """AST代码解析器 - 基于抽象语法树深度提取代码结构"""

    def parse(self, file_path: str, language: str = None) -> CodeStructure:
        """解析代码文件，提取完整结构"""
        if language is None:
            language = self._detect_language(file_path)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        structure = CodeStructure(
            filename=os.path.basename(file_path),
            language=language,
            total_lines=source.count('\n') + 1
        )

        parser = {
            'python': self._parse_python,
            'java': self._parse_java,
            'c': self._parse_c,
            'cpp': self._parse_cpp,
            'csharp': self._parse_csharp,
        }.get(language)

        if parser:
            try:
                parser(source, structure)
            except Exception as e:
                logger.error(f"AST解析失败: {file_path}, 语言: {language}, 错误: {str(e)}")
                self._regex_fallback(source, language, structure)
        else:
            self._regex_fallback(source, language, structure)

        # 构建调用图和继承图
        self._build_graphs(structure)
        structure.total_functions = len([e for e in structure.entities if e.entity_type in ('function', 'method')])
        structure.total_classes = len([e for e in structure.entities if e.entity_type == 'class'])

        return structure

    def _parse_python(self, source: str, structure: CodeStructure):
        """Python AST解析"""
        tree = ast.parse(source)
        lines = source.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    structure.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    structure.imports.append(f"{module}.{alias.name}")

            elif isinstance(node, ast.ClassDef):
                entity = CodeEntity(
                    name=node.name,
                    entity_type='class',
                    language='python',
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    source_code='\n'.join(lines[node.lineno - 1:(node.end_lineno or node.lineno)]),
                    docstring=ast.get_docstring(node) or '',
                    base_classes=[self._get_name(b) for b in node.bases],
                    modifiers=['public']
                )
                # 提取类方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method = CodeEntity(
                            name=f"{node.name}.{item.name}",
                            entity_type='method',
                            language='python',
                            start_line=item.lineno,
                            end_line=item.end_lineno or item.lineno,
                            source_code='\n'.join(lines[item.lineno - 1:(item.end_lineno or item.lineno)]),
                            docstring=ast.get_docstring(item) or '',
                            parameters=self._extract_python_params(item),
                            return_type=self._get_annotation(item.returns) if item.returns else '',
                            calls=self._extract_python_calls(item),
                            modifiers=['private' if item.name.startswith('_') else 'public']
                        )
                        structure.entities.append(method)
                structure.entities.append(entity)

            elif isinstance(node, ast.FunctionDef) and not hasattr(node, '_parent_class'):
                # 顶层函数
                entity = CodeEntity(
                    name=node.name,
                    entity_type='function',
                    language='python',
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    source_code='\n'.join(lines[node.lineno - 1:(node.end_lineno or node.lineno)]),
                    docstring=ast.get_docstring(node) or '',
                    parameters=self._extract_python_params(node),
                    return_type=self._get_annotation(node.returns) if node.returns else '',
                    calls=self._extract_python_calls(node),
                    modifiers=['private' if node.name.startswith('_') else 'public']
                )
                structure.entities.append(entity)

    def _extract_python_params(self, node) -> List[Dict]:
        """提取Python函数参数"""
        params = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': self._get_annotation(arg.annotation) if arg.annotation else ''
            }
            params.append(param)
        return params

    def _extract_python_calls(self, node) -> List[str]:
        """提取Python函数调用"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = self._get_call_name(child)
                if call_name:
                    calls.append(call_name)
        return list(set(calls))

    def _get_call_name(self, node) -> str:
        """获取调用名称"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ''

    def _get_name(self, node) -> str:
        """获取AST节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ''

    def _get_annotation(self, node) -> str:
        """获取类型注解字符串"""
        if node is None:
            return ''
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        return ast.unparse(node) if hasattr(ast, 'unparse') else ''

    def _parse_java(self, source: str, structure: CodeStructure):
        """Java代码解析（基于正则+结构化匹配）"""
        self._parse_c_like(source, structure, 'java')

    def _parse_c(self, source: str, structure: CodeStructure):
        """C代码解析"""
        self._parse_c_like(source, structure, 'c')

    def _parse_cpp(self, source: str, structure: CodeStructure):
        """C++代码解析"""
        self._parse_c_like(source, structure, 'cpp')

    def _parse_csharp(self, source: str, structure: CodeStructure):
        """C#代码解析"""
        self._parse_c_like(source, structure, 'csharp')

    def _parse_c_like(self, source: str, structure: CodeStructure, language: str):
        """C系语言解析 - 基于正则的结构化提取"""
        lines = source.split('\n')

        # 提取import/include
        if language == 'java':
            for match in re.finditer(r'import\s+([\w.]+)\s*;', source):
                structure.imports.append(match.group(1))
        elif language in ('c', 'cpp'):
            for match in re.finditer(r'#include\s*[<"]([^>"]+)[>"]', source):
                structure.imports.append(match.group(1))
        elif language == 'csharp':
            for match in re.finditer(r'using\s+([\w.]+)\s*;', source):
                structure.imports.append(match.group(1))

        # 提取类定义
        class_pattern = {
            'java': r'(?:public|private|protected)?\s*(?:abstract\s+)?(?:final\s+)?(?:class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?',
            'csharp': r'(?:public|private|protected|internal)?\s*(?:abstract\s+)?(?:sealed\s+)?(?:class|interface|struct)\s+(\w+)(?:\s*:\s*([\w\s,]+))?',
            'cpp': r'(?:class|struct)\s+(\w+)\s*(?::\s*(?:public|private|protected)\s+(\w+))?',
            'c': r'(?:typedef\s+)?struct\s+(\w+)',
        }

        pattern = class_pattern.get(language, class_pattern['java'])
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            base_class = match.group(2) if match.lastindex >= 2 else ''
            start_line = source[:match.start()].count('\n') + 1

            # 查找类结束位置（简化：通过花括号匹配）
            end_line = self._find_block_end(source, match.start())

            # 提取类注释
            docstring = self._extract_preceding_comment(source, match.start())

            entity = CodeEntity(
                name=class_name,
                entity_type='class',
                language=language,
                start_line=start_line,
                end_line=end_line,
                source_code='\n'.join(lines[start_line - 1:end_line]),
                docstring=docstring,
                base_classes=[base_class] if base_class else [],
                modifiers=self._extract_modifiers(match.group(0))
            )
            structure.entities.append(entity)

        # 提取函数/方法定义
        func_patterns = {
            'java': r'(?:(?:public|private|protected)\s+)?(?:(?:static|final|abstract|synchronized)\s+)*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)',
            'c': r'(?:(?:static|extern|inline)\s+)*(\w+(?:\s*\*)*)\s+(\w+)\s*\(([^)]*)\)',
            'cpp': r'(?:(?:(?:static|virtual|inline|const|override)\s+)*)(\w+(?:\s*[&*])*)\s+(\w+)\s*\(([^)]*)\)',
            'csharp': r'(?:(?:public|private|protected|internal)\s+)?(?:(?:static|virtual|override|abstract|async)\s+)*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)',
        }

        func_pattern = func_patterns.get(language, func_patterns['java'])
        for match in re.finditer(func_pattern, source):
            return_type = match.group(1).strip()
            func_name = match.group(2).strip()
            params_str = match.group(3).strip()

            # 过滤掉关键字
            skip_names = {'if', 'while', 'for', 'switch', 'catch', 'class', 'return', 'new'}
            if func_name in skip_names:
                continue

            start_line = source[:match.start()].count('\n') + 1
            end_line = self._find_block_end(source, match.start())
            docstring = self._extract_preceding_comment(source, match.start())

            # 解析参数
            parameters = self._parse_c_params(params_str)

            entity = CodeEntity(
                name=func_name,
                entity_type='method' if '.' in func_name or '::' in func_name else 'function',
                language=language,
                start_line=start_line,
                end_line=end_line,
                source_code='\n'.join(lines[start_line - 1:min(end_line, start_line + 50)]),
                docstring=docstring,
                parameters=parameters,
                return_type=return_type,
                modifiers=self._extract_modifiers(match.group(0))
            )
            structure.entities.append(entity)

    def _parse_c_params(self, params_str: str) -> List[Dict]:
        """解析C系语言函数参数"""
        if not params_str.strip():
            return []
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if not param:
                continue
            parts = param.rsplit(None, 1)
            if len(parts) >= 2:
                params.append({'type': parts[0].strip(), 'name': parts[1].strip(' *&')})
            else:
                params.append({'type': '', 'name': param.strip()})
        return params

    def _regex_fallback(self, source: str, language: str, structure: CodeStructure):
        """正则回退解析"""
        lines = source.split('\n')
        # 通用函数提取
        for match in re.finditer(r'(?:function|def|func|fn)\s+(\w+)\s*\(([^)]*)\)', source):
            name = match.group(1)
            start_line = source[:match.start()].count('\n') + 1
            entity = CodeEntity(
                name=name, entity_type='function', language=language,
                start_line=start_line, end_line=start_line + 10
            )
            structure.entities.append(entity)

    def _find_block_end(self, source: str, start_pos: int) -> int:
        """查找代码块结束行"""
        brace_count = 0
        found_open = False
        for i in range(start_pos, min(start_pos + 5000, len(source))):
            if source[i] == '{':
                brace_count += 1
                found_open = True
            elif source[i] == '}':
                brace_count -= 1
                if found_open and brace_count == 0:
                    return source[:i].count('\n') + 1
        return source[:start_pos].count('\n') + 20

    def _extract_preceding_comment(self, source: str, pos: int) -> str:
        """提取代码前的注释"""
        before = source[:pos].rstrip()
        # 块注释
        block_match = re.search(r'/\*([\s\S]*?)\*/\s*$', before)
        if block_match:
            return block_match.group(1).strip()
        # 行注释
        lines = before.split('\n')
        comment_lines = []
        for line in reversed(lines):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                comment_lines.insert(0, stripped.lstrip('/# '))
            else:
                break
        return '\n'.join(comment_lines)

    def _extract_modifiers(self, text: str) -> List[str]:
        """提取修饰符"""
        modifiers = []
        modifier_keywords = {'public', 'private', 'protected', 'static', 'final',
                             'abstract', 'virtual', 'override', 'sealed', 'async',
                             'const', 'inline', 'extern', 'synchronized', 'internal'}
        for word in text.split():
            if word.lower() in modifier_keywords:
                modifiers.append(word.lower())
        return modifiers

    def _build_graphs(self, structure: CodeStructure):
        """构建调用图和继承图"""
        for entity in structure.entities:
            if entity.entity_type == 'class' and entity.base_classes:
                structure.inheritance_graph[entity.name] = entity.base_classes
            if entity.calls:
                structure.call_graph[entity.name] = entity.calls

    def _detect_language(self, file_path: str) -> str:
        """检测代码语言"""
        ext_map = {
            '.py': 'python', '.java': 'java', '.c': 'c', '.h': 'c',
            '.cpp': 'cpp', '.hpp': 'cpp', '.cc': 'cpp',
            '.cs': 'csharp', '.go': 'go', '.rs': 'rust',
            '.js': 'javascript', '.ts': 'typescript'
        }
        ext = os.path.splitext(file_path)[1].lower()
        return ext_map.get(ext, 'unknown')

    def get_code_chunks(self, structure: CodeStructure) -> List[Dict]:
        """按函数/类/模块粒度进行代码分块，保留调用关系与上下文逻辑"""
        chunks = []

        for entity in structure.entities:
            # 获取父级上下文
            parent_context = ''
            if entity.entity_type == 'method' and '.' in entity.name:
                parent_class = entity.name.split('.')[0]
                parent_context = f"类: {parent_class}"

            # 获取调用关系上下文
            call_context = ''
            if entity.calls:
                call_context = f"调用: {', '.join(entity.calls[:10])}"

            # 获取继承关系上下文
            inheritance_context = ''
            if entity.base_classes:
                inheritance_context = f"继承自: {', '.join(entity.base_classes)}"

            # 构建元数据
            metadata = {
                'entity_name': entity.name,
                'entity_type': entity.entity_type,
                'language': structure.language,
                'filename': structure.filename,
                'start_line': entity.start_line,
                'end_line': entity.end_line,
                'parent_context': parent_context,
                'call_context': call_context,
                'inheritance_context': inheritance_context,
                'docstring': entity.docstring,
                'parameters': entity.parameters,
                'return_type': entity.return_type,
                'modifiers': entity.modifiers,
            }

            # 构建分块内容（含上下文头）
            header_parts = [f"[{entity.entity_type.upper()}] {entity.name}"]
            if parent_context:
                header_parts.append(parent_context)
            if inheritance_context:
                header_parts.append(inheritance_context)
            if call_context:
                header_parts.append(call_context)
            if entity.docstring:
                header_parts.append(f"说明: {entity.docstring}")
            if entity.parameters:
                param_str = ', '.join([f"{p.get('type', '')} {p.get('name', '')}".strip() for p in entity.parameters])
                header_parts.append(f"参数: ({param_str})")
            if entity.return_type:
                header_parts.append(f"返回: {entity.return_type}")

            content = '\n'.join(header_parts) + '\n\n' + entity.source_code

            chunks.append({
                'content': content,
                'metadata': metadata,
                'chunk_type': 'code_entity'
            })

        return chunks
