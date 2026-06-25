"""测试438C模板文档解析"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.document_parser import DocumentParser

parser = DocumentParser()
templates_dir = r'f:\geovis\cerateWord\438c'

for f in sorted(os.listdir(templates_dir)):
    if f.startswith('~'):
        continue
    path = os.path.join(templates_dir, f)
    result = parser.parse(path)
    struct = result.get('structure', {})
    text_len = len(result.get('text', ''))
    error = result.get('error', 'none')
    ftype = struct.get('type', 'unknown')
    paras = len(struct.get('paragraphs', []))
    tables = len(struct.get('tables', []))
    print(f'{f}')
    print(f'  type={ftype}, text_len={text_len}, paragraphs={paras}, tables={tables}, error={error}')
    if text_len > 0:
        print(f'  preview: {result.get("text", "")[:200]}...')
    print()
