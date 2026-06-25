"""端到端测试：知识库构建全流程（简化版）"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.models import KnowledgeBase, KnowledgeFile, Project

app = create_app()
app.config['TESTING'] = True

with app.app_context():
    db.create_all()

    # 清理旧数据
    KnowledgeFile.query.delete()
    KnowledgeBase.query.delete()
    Project.query.delete()
    db.session.commit()

    client = app.test_client()

    # 1. 创建项目
    print('=== 1. 创建项目 ===')
    r = client.post('/api/project/projects', json={
        'name': '438C文档项目', 'system_name': '测试系统', 'organization': '中科星图'
    })
    proj = r.get_json()
    pid = proj['id']
    print(f'  OK: id={pid}, name={proj["name"]}')

    # 2. 创建知识库
    print('\n=== 2. 创建知识库 ===')
    r = client.post('/api/knowledge/bases', json={
        'name': '438C标准知识库', 'description': '包含438C标准文档和模板',
        'project_id': pid, 'kb_type': '438c_standard', 'security_level': '内部',
        'tags': ['438C', '标准']
    })
    kb = r.get_json()
    kb_id = kb['id']
    print(f'  OK: id={kb_id}, name={kb["name"]}')

    # 3. 知识库列表
    print('\n=== 3. 知识库列表 ===')
    r = client.get('/api/knowledge/bases')
    kbs = r.get_json()
    print(f'  OK: total={kbs["total"]}')

    # 4. 批量导入438C模板文件
    print('\n=== 4. 批量导入438C模板文件 ===')
    templates_dir = r'f:\geovis\cerateWord\438c'
    file_paths = []
    count = 0
    for fname in sorted(os.listdir(templates_dir)):
        if fname.startswith('~') or not fname.endswith('.docx'):
            continue
        if count >= 2:
            break
        file_paths.append(os.path.join(templates_dir, fname))
        count += 1

    if file_paths:
        r = client.post(f'/api/knowledge/bases/{kb_id}/batch-import', json={
            'file_paths': file_paths,
            'tags': ['438C', '标准']
        })
        result = r.get_json()
        print(f'  OK: imported={len(result.get("results", []))}')
        for item in result.get('results', []):
            print(f'  - {item.get("filename", "?")}: status={item.get("status", "?")}, chunks={item.get("chunk_count", 0)}')
    else:
        print('  无docx文件可导入')

    # 5. 文件列表
    print('\n=== 5. 文件列表 ===')
    r = client.get(f'/api/knowledge/bases/{kb_id}/files')
    files_data = r.get_json()
    print(f'  OK: total={files_data["total"]}')
    for f in files_data['items']:
        print(f'  - {f["original_filename"]}: type={f["file_type"]}, '
              f'chunks={f["chunk_count"]}, review={f["review_status"]}, index={f["index_status"]}')

    # 6. 审核文件
    print('\n=== 6. 审核文件 ===')
    if files_data['items']:
        fid = files_data['items'][0]['id']
        r = client.post(f'/api/knowledge/files/{fid}/review', json={
            'action': 'approve', 'reviewer': 'admin', 'comments': '审核通过'
        })
        result = r.get_json()
        print(f'  OK: review_status={result["review_status"]}')

    # 7. 语义搜索
    print('\n=== 7. 语义搜索 ===')
    r = client.post(f'/api/knowledge/bases/{kb_id}/search', json={
        'query': '软件开发计划', 'top_k': 3, 'use_rerank': False
    })
    search = r.get_json()
    print(f'  OK: total={search["total"]}')
    for s in search.get('results', []):
        content = s.get('content', '')[:80]
        score = s.get('score', 0)
        print(f'  - score={score:.3f}, content: {content}...')

    # 8. 预览文件
    print('\n=== 8. 预览文件 ===')
    if files_data['items']:
        fid = files_data['items'][0]['id']
        r = client.get(f'/api/knowledge/files/{fid}/preview')
        preview = r.get_json()
        print(f'  OK: filename={preview["filename"]}, content_len={len(preview.get("content_text", ""))}')

    # 9. 知识库详情
    print('\n=== 9. 知识库详情 ===')
    r = client.get(f'/api/knowledge/bases/{kb_id}')
    detail = r.get_json()
    print(f'  OK: name={detail["name"]}, docs={detail["doc_count"]}, size={detail["total_size"]}')

    # 10. 编辑文件内容
    print('\n=== 10. 编辑文件内容 ===')
    if files_data['items']:
        fid = files_data['items'][0]['id']
        r = client.put(f'/api/knowledge/files/{fid}/edit', json={
            'content_text': '编辑后的测试内容 - 软件开发计划更新版',
            'reviewer': 'admin'
        })
        result = r.get_json()
        print(f'  OK: version=v{result.get("version_number", "?")}')

    # 11. 版本历史
    print('\n=== 11. 版本历史 ===')
    if files_data['items']:
        fid = files_data['items'][0]['id']
        r = client.get(f'/api/knowledge/files/{fid}/versions')
        versions = r.get_json()
        print(f'  OK: total={versions["total"]}')
        for v in versions.get('items', []):
            print(f'  - v{v["version_number"]}: {v["change_type"]} by {v["changed_by"]}')

    # 12. 审核记录
    print('\n=== 12. 审核记录 ===')
    r = client.get('/api/knowledge/review-records')
    records = r.get_json()
    print(f'  OK: total={records["total"]}')

    print('\n' + '=' * 60)
    print('全部测试完成!')
    print('=' * 60)
