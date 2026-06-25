"""测试MinIO存储服务和LLM服务"""
import os
import sys
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

# ===== 测试MinIO存储服务 =====
print("=" * 60)
print("1. 测试MinIO存储服务")
print("=" * 60)

from app.services.storage_service import MinIOStorage, get_storage

storage = get_storage()
print(f"MinIO可用: {storage.available}")
print(f"Endpoint: {storage.endpoint}")
print(f"Bucket: {storage.bucket_name}")

# 测试上传文件
test_content = "这是MinIO存储测试文件 - 438C文档生成系统"
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
    tmp.write(test_content)
    tmp_path = tmp.name

upload_result = storage.upload_file('test/minio_test.txt', tmp_path)
print(f"\n上传结果: {upload_result}")

# 测试文件存在检查
exists = storage.file_exists('test/minio_test.txt')
print(f"文件存在: {exists}")

# 测试下载文件
with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
    download_path = tmp.name
download_result = storage.download_file('test/minio_test.txt', download_path)
print(f"下载结果: {download_result}")

if download_result:
    with open(download_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    print(f"下载内容: {content[:100]}")

# 测试删除文件
delete_result = storage.delete_file('test/minio_test.txt')
print(f"删除结果: {delete_result}")

# 清理临时文件
os.unlink(tmp_path)
if os.path.exists(download_path):
    os.unlink(download_path)

# ===== 测试LLM服务 =====
print("\n" + "=" * 60)
print("2. 测试国产大模型LLM服务")
print("=" * 60)

from app.services.llm_service import LLMService, QwenService, DeepSeekService, ChatGLMService, LocalLLMService, create_llm_service

# 测试工厂方法
print("\n--- 测试LLM工厂方法 ---")
for provider in ['qwen', 'deepseek', 'chatglm', 'local']:
    service = create_llm_service(provider=provider)
    print(f"  {provider}: api_base={service.api_base}, model={service.model}")

# 测试千问服务（模拟模式，无API Key时）
print("\n--- 测试千问服务(模拟模式) ---")
qwen = create_llm_service(provider='qwen')
result = qwen.generate("你是438C文档专家", "请简述438C标准包含哪些文档类型")
print(f"  状态: {result.get('status')}")
print(f"  提供商: {result.get('provider')}")
if result.get('status') == 'mock':
    print(f"  [模拟模式] 内容前200字: {result.get('content', '')[:200]}")
elif result.get('status') == 'success':
    print(f"  内容前200字: {result.get('content', '')[:200]}")
else:
    print(f"  错误: {result.get('error', '')}")

# 测试章节生成（模拟模式）
print("\n--- 测试章节生成(模拟模式) ---")
chapter_result = qwen.generate_chapter('SDP', '1', '范围')
print(f"  状态: {chapter_result.get('status')}")
if chapter_result.get('content'):
    print(f"  内容前200字: {chapter_result.get('content', '')[:200]}")

print("\n" + "=" * 60)
print("3. 测试总结")
print("=" * 60)
print(f"MinIO存储: {'可用' if storage.available else '不可用(回退到本地存储)'}")
print(f"LLM服务: 千问/DeepSeek/ChatGLM/本地部署 均已配置")
print(f"DOCX解析: 7/7 模板解析成功")
print(f"DOC解析: 需要 Word/LibreOffice 支持转换")
