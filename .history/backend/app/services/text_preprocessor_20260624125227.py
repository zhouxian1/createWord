"""文本预处理服务 - 去重、去无关符号、敏感词过滤、代码注释标准化"""
import re
import hashlib
import logging
from typing import List, Dict, Set, Tuple, Optional

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """文本预处理器 - 对解析文本进行清洗和标准化"""

    # 军标敏感词库（示例，实际应从配置加载）
    DEFAULT_SENSITIVE_WORDS = [
        '机密', '绝密', '秘密', '内部'
    ]

    # 无关符号模式
    NOISE_PATTERNS = [
        r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',  # 控制字符
        r'\u3000{2,}',  # 连续全角空格
        r'[ \t]{4,}',  # 连续半角空格/Tab
        r'\n{3,}',  # 连续3个以上换行
        r'[\ufeff\ufffe]',  # BOM字符
        r'第\s*\d+\s*页\s*/\s*\d+\s*页',  # 页码标记
        r'共\s*\d+\s*页',  # 总页数标记
        r'-\s*\d+\s*-',  # 简单页码
    ]

    # 代码注释标准化模式
    COMMENT_PATTERNS = {
        'python': {
            'docstring': r'"""([\s\S]*?)"""',
            'inline': r'#\s*(.+)',
        },
        'java': {
            'javadoc': r'/\*\*([\s\S]*?)\*/',
            'block': r'/\*([\s\S]*?)\*/',
            'inline': r'//\s*(.+)',
        },
        'c': {
            'block': r'/\*([\s\S]*?)\*/',
            'inline': r'//\s*(.+)',
        },
        'cpp': {
            'block': r'/\*([\s\S]*?)\*/',
            'inline': r'//\s*(.+)',
        },
        'csharp': {
            'xmldoc': r'///\s*(.+)',
            'block': r'/\*([\s\S]*?)\*/',
            'inline': r'//\s*(.+)',
        }
    }

    def __init__(self, sensitive_words: List[str] = None, enable_dedup: bool = True,
                 enable_noise_removal: bool = True, enable_sensitive_filter: bool = True):
        self.sensitive_words = set(sensitive_words or self.DEFAULT_SENSITIVE_WORDS)
        self.enable_dedup = enable_dedup
        self.enable_noise_removal = enable_noise_removal
        self.enable_sensitive_filter = enable_sensitive_filter
        self._seen_hashes: Set[str] = set()

    def preprocess(self, text: str, file_type: str = '', options: Dict = None) -> Dict:
        """对文本进行完整预处理流水线"""
        opts = options or {}
        original_length = len(text)

        # 1. 去除无关符号和噪声
        if self.enable_noise_removal:
            text = self.remove_noise(text)

        # 2. 去重
        if self.enable_dedup:
            text = self.deduplicate(text)

        # 3. 敏感词过滤
        if self.enable_sensitive_filter and not opts.get('skip_sensitive'):
            text, sensitive_found = self.filter_sensitive(text)
        else:
            sensitive_found = []

        # 4. 代码注释标准化
        if file_type in ('python_code', 'java_code', 'c_code', 'cpp_code', 'dotnet_code'):
            text = self.standardize_code_comments(text, file_type)

        return {
            'text': text,
            'original_length': original_length,
            'processed_length': len(text),
            'reduction_ratio': round(1 - len(text) / max(original_length, 1), 4),
            'sensitive_words_found': sensitive_found if self.enable_sensitive_filter else []
        }

    def remove_noise(self, text: str) -> str:
        """去除无关符号和噪声"""
        for pattern in self.NOISE_PATTERNS:
            text = re.sub(pattern, '', text)

        # 标准化空白字符
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)

        # 去除行首尾空白
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()

    def deduplicate(self, text: str) -> str:
        """文本去重 - 基于段落级哈希去重"""
        paragraphs = text.split('\n')
        seen = set()
        unique_paragraphs = []

        for para in paragraphs:
            para_stripped = para.strip()
            if not para_stripped:
                unique_paragraphs.append(para)
                continue

            # 计算段落哈希
            para_hash = hashlib.md5(para_stripped.encode('utf-8')).hexdigest()

            if para_hash not in seen:
                seen.add(para_hash)
                unique_paragraphs.append(para)
            # 重复段落跳过

        return '\n'.join(unique_paragraphs)

    def filter_sensitive(self, text: str) -> Tuple[str, List[str]]:
        """敏感词过滤 - 替换为***"""
        found = []
        for word in self.sensitive_words:
            if word in text:
                found.append(word)
                text = text.replace(word, '*' * len(word))
        return text, found

    def standardize_code_comments(self, code: str, file_type: str) -> str:
        """标准化代码注释格式"""
        lang_map = {
            'python_code': 'python',
            'java_code': 'java',
            'c_code': 'c',
            'cpp_code': 'cpp',
            'dotnet_code': 'csharp'
        }
        lang = lang_map.get(file_type, '')

        if lang not in self.COMMENT_PATTERNS:
            return code

        patterns = self.COMMENT_PATTERNS[lang]

        # 标准化块注释 - 确保格式统一
        if 'block' in patterns:
            def clean_block_comment(match):
                content = match.group(1).strip()
                lines = [l.strip().lstrip('*').strip() for l in content.split('\n') if l.strip()]
                return '/* ' + '\n * '.join(lines) + ' */'
            code = re.sub(patterns['block'], clean_block_comment, code, flags=re.DOTALL)

        # 标准化行内注释 - 去除多余空白
        if 'inline' in patterns:
            def clean_inline_comment(match):
                content = match.group(1).strip()
                prefix = '//' if lang != 'python' else '#'
                return f'{prefix} {content}'
            code = re.sub(patterns['inline'], clean_inline_comment, code)

        # 标准化Javadoc/文档注释
        if 'javadoc' in patterns:
            def clean_javadoc(match):
                content = match.group(1).strip()
                lines = [l.strip().lstrip('*').strip() for l in content.split('\n') if l.strip()]
                return '/**\n' + '\n'.join(f' * {l}' for l in lines) + '\n */'
            code = re.sub(patterns['javadoc'], clean_javadoc, code, flags=re.DOTALL)

        return code

    def add_sensitive_words(self, words: List[str]):
        """添加敏感词"""
        self.sensitive_words.update(words)

    def remove_sensitive_words(self, words: List[str]):
        """移除敏感词"""
        self.sensitive_words -= set(words)

    def reset_dedup(self):
        """重置去重缓存"""
        self._seen_hashes.clear()
