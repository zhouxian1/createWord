"""测试438C模板文档解析 - 仅DOCX"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.document_parser import DocumentParser

parser = DocumentParser()
templates_dir = r'f:\geovis\cerateWord\438c'

for f in sorted(os.listdir(templates_dir)):
    if f.startswith('~') or not f.endswith('.docx'):
        continue
    path = os.path.join(templates_dir, f)
    result = parser.parse(path)
    struct = result.get('structure', {})
    text_len = len(result.get('text', ''))
    paras = len(struct.get('paragraphs', []))
    tables = len(struct.get('tables', []))
    print(f'{f}: text={text_len}, paras={paras}, tables={tables}')
