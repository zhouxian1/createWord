"""端到端测试：知识库构建全流程"""
import requests
import json
import os
import sys

base = 'http://127.0.0.1:5000/api'

def test():
    # 1. 创建项目
    print('=== 1. 创建项目 ===')
    r = requests.post(f'{base}/project/projects', json={
        'name': '438C文档项目', 'system_name': '测试系统', 'organization': '中科星图'
    })
    proj = r.json()
    pid = proj['id']
    print(f'  项目: id={pid}, name={proj["name"]}')

    # 2. 创建知识库
    print('\n=== 2. 创建知识库 ===')
    r = requests.post(f'{base}/knowledge/bases', json={
        'name': '438C标准知识库', 'description': '包含438C标准文档和模板',
        'project_id': pid, 'kb_type': '438c_standard', 'security_level': '内部',
        'tags': ['438C', '标准']
    })
    kb = r.json()
    kb_id = kb['id']
    print(f'  知识库: id={kb_id}, name={kb["name"]}')

    # 3. 获取知识库列表
    print('\n=== 3. 知识库列表 ===')
    r = requests.get(f'{base}/knowledge/bases')
    kbs = r.json()
    print(f'  总数: {kbs["total"]}')
    for b in kbs['items']:
        print(f'  - {b["name"]} (type={b["kb_type"]}, docs={b["doc_count"]})')

    # 4. 上传438C模板文件
    print('\n=== 4. 上传438C模板文件 ===')
    templates_dir = r'f:\geovis\cerateWord\438c'
    uploaded = 0
    for fname in sorted(os.listdir(templates_dir)):
        if fname.startswith('~') or not fname.endswith('.docx'):
            continue
        if uploaded >= 3:  # 只上传前3个
            break
        path = os.path.join(templates_dir, fname)
        with open(path, 'rb') as fp:
            r = requests.post(f'{base}/knowledge/bases/{kb_id}/upload',
                files={'files': (fname, fp, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
        result = r.json()
        for item in result.get('results', []):
            print(f'  {item["filename"]}: status={item["status"]}, chunks={item.get("chunk_count", 0)}')
        uploaded += 1

    # 5. 获取文件列表
    print('\n=== 5. 文件列表 ===')
    r = requests.get(f'{base}/knowledge/bases/{kb_id}/files')
    files_data = r.json()
    print(f'  总数: {files_data["total"]}')
    for f in files_data['items']:
        print(f'  - {f["original_filename"]}: type={f["file_type"]}, '
              f'size={f["file_size"]}, chunks={f["chunk_count"]}, '
              f'review={f["review_status"]}, index={f["index_status"]}')

    # 6. 审核文件
    print('\n=== 6. 审核文件 ===')
    if files_data['items']:
        fid = files_data['items'][0]['id']
        r = requests.post(f'{base}/knowledge/files/{fid}/review', json={
            'action': 'approve', 'reviewer': 'admin', 'comments': '审核通过'
        })
        result = r.json()
        print(f'  审核结果: review_status={result["review_status"]}')

    # 7. 语义搜索
    print('\n=== 7. 语义搜索 ===')
    r = requests.post(f'{base}/knowledge/bases/{kb_id}/search', json={
        'query': '软件开发计划', 'top_k': 3, 'use_rerank': False
    })
    search = r.json()
    print(f'  搜索结果: {search["total"]}条')
    for s in search.get('results', []):
        content = s.get('content', '')[:100]
        print(f'  - {content}...')

    # 8. 预览文件
    print('\n=== 8. 预览文件 ===')
    if files_data['items']:
        fid = files_data['items'][0]['id']
        r = requests.get(f'{base}/knowledge/files/{fid}/preview')
        preview = r.json()
        print(f'  文件: {preview["filename"]}')
        print(f'  内容长度: {len(preview.get("content_text", ""))}')
        print(f'  分块数: {preview.get("chunk_count", 0)}')

    # 9. 获取知识库详情
    print('\n=== 9. 知识库详情 ===')
    r = requests.get(f'{base}/knowledge/bases/{kb_id}')
    detail = r.json()
    print(f'  名称: {detail["name"]}')
    print(f'  文件数: {detail["doc_count"]}')
    print(f'  总大小: {detail["total_size"]}')

    print('\n=== 全部测试完成 ===')

if __name__ == '__main__':
    test()
