"""快速测试storage和docx解析"""
import os, sys
sys.path.insert(0, '.')

from app.services.storage_service import get_storage
from app.services.document_parser import DocumentParser

# 测试storage
print("1. 测试storage...")
storage = get_storage()
print(f"   storage type: {type(storage).__name__}")

# 测试docx解析
print("\n2. 测试docx解析...")
templates_dir = r'f:\geovis\cerateWord\438c'
for fname in sorted(os.listdir(templates_dir))[:1]:
    if fname.endswith('.docx') and not fname.startswith('~'):
        path = os.path.join(templates_dir, fname)
        print(f"   解析: {fname}")
        parser = DocumentParser()
        result = parser.parse(path)
        text = result.get('text', '')
        print(f"   文本长度: {len(text)}")
        print(f"   前100字: {text[:100]}")

# 测试上传
print("\n3. 测试上传...")
for fname in sorted(os.listdir(templates_dir))[:1]:
    if fname.endswith('.docx') and not fname.startswith('~'):
        path = os.path.join(templates_dir, fname)
        import uuid
        object_name = f"knowledge/test/{uuid.uuid4().hex}.docx"
        result = storage.upload_file(object_name, path)
        print(f"   上传结果: {result}")

print("\n完成!")
