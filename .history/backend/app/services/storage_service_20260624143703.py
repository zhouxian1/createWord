"""MinIO对象存储服务 - 替代本地文件存储"""
import os
import io
import logging
from typing import Optional, BinaryIO
from datetime import timedelta

logger = logging.getLogger(__name__)


class MinIOStorage:
    """MinIO对象存储服务"""

    def __init__(self, endpoint=None, access_key=None, secret_key=None,
                 bucket_name=None, secure=False):
        self.endpoint = endpoint or os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = access_key or os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = secret_key or os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
        self.bucket_name = bucket_name or os.environ.get('MINIO_BUCKET', 'doc-gen-system')
        self.secure = secure or os.environ.get('MINIO_SECURE', 'false').lower() == 'true'
        self._client = None

    def _get_client(self):
        """获取MinIO客户端（延迟初始化）"""
        if self._client is None:
            try:
                from minio import Minio
                self._client = Minio(
                    self.endpoint,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=self.secure
                )
                # 确保bucket存在
                if not self._client.bucket_exists(self.bucket_name):
                    self._client.make_bucket(self.bucket_name)
                    logger.info(f"创建MinIO bucket: {self.bucket_name}")
            except ImportError:
                logger.warning("minio库未安装，回退到本地文件存储")
                self._client = None
            except Exception as e:
                logger.error(f"MinIO连接失败: {str(e)}，回退到本地文件存储")
                self._client = None
        return self._client

    @property
    def available(self) -> bool:
        """MinIO是否可用"""
        return self._get_client() is not None

    def upload_file(self, object_name: str, file_path: str, content_type: str = 'application/octet-stream') -> dict:
        """上传本地文件到MinIO"""
        client = self._get_client()
        if client is None:
            return self._local_upload_fallback(object_name, file_path)

        try:
            from minio.commonconfig import Tags
            result = client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type=content_type
            )
            logger.info(f"上传文件到MinIO: {object_name}, ETag: {result.etag}")
            return {
                'storage_type': 'minio',
                'object_name': object_name,
                'etag': result.etag,
                'bucket': self.bucket_name
            }
        except Exception as e:
            logger.error(f"MinIO上传失败: {str(e)}，回退到本地存储")
            return self._local_upload_fallback(object_name, file_path)

    def upload_bytes(self, object_name: str, data: bytes, content_type: str = 'application/octet-stream') -> dict:
        """上传字节数据到MinIO"""
        client = self._get_client()
        if client is None:
            return self._local_upload_bytes_fallback(object_name, data)

        try:
            data_stream = io.BytesIO(data)
            result = client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length=len(data),
                content_type=content_type
            )
            return {
                'storage_type': 'minio',
                'object_name': object_name,
                'etag': result.etag,
                'bucket': self.bucket_name
            }
        except Exception as e:
            logger.error(f"MinIO上传字节失败: {str(e)}，回退到本地存储")
            return self._local_upload_bytes_fallback(object_name, data)

    def download_file(self, object_name: str, file_path: str) -> bool:
        """从MinIO下载文件到本地"""
        client = self._get_client()
        if client is None:
            return self._local_download_fallback(object_name, file_path)

        try:
            client.fget_object(self.bucket_name, object_name, file_path)
            return True
        except Exception as e:
            logger.error(f"MinIO下载失败: {str(e)}")
            return self._local_download_fallback(object_name, file_path)

    def download_bytes(self, object_name: str) -> Optional[bytes]:
        """从MinIO下载文件为字节数据"""
        client = self._get_client()
        if client is None:
            return self._local_download_bytes_fallback(object_name)

        try:
            response = client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            logger.error(f"MinIO下载字节失败: {str(e)}")
            return self._local_download_bytes_fallback(object_name)

    def delete_file(self, object_name: str) -> bool:
        """从MinIO删除文件"""
        client = self._get_client()
        if client is None:
            return self._local_delete_fallback(object_name)

        try:
            client.remove_object(self.bucket_name, object_name)
            return True
        except Exception as e:
            logger.error(f"MinIO删除失败: {str(e)}")
            return self._local_delete_fallback(object_name)

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """获取预签名URL（临时访问链接）"""
        client = self._get_client()
        if client is None:
            return None

        try:
            url = client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except Exception as e:
            logger.error(f"获取预签名URL失败: {str(e)}")
            return None

    def file_exists(self, object_name: str) -> bool:
        """检查文件是否存在"""
        client = self._get_client()
        if client is None:
            local_path = self._get_local_path(object_name)
            return os.path.exists(local_path)

        try:
            client.stat_object(self.bucket_name, object_name)
            return True
        except Exception:
            return False

    def list_objects(self, prefix: str = '', recursive: bool = True) -> list:
        """列出指定前缀下的所有对象"""
        client = self._get_client()
        if client is None:
            return self._local_list_fallback(prefix)

        try:
            objects = client.list_objects(self.bucket_name, prefix=prefix, recursive=recursive)
            return [{'object_name': obj.object_name, 'size': obj.size, 'last_modified': obj.last_modified}
                    for obj in objects]
        except Exception as e:
            logger.error(f"MinIO列表失败: {str(e)}")
            return self._local_list_fallback(prefix)

    def copy_object(self, source_name: str, dest_name: str) -> bool:
        """复制对象"""
        client = self._get_client()
        if client is None:
            return self._local_copy_fallback(source_name, dest_name)

        try:
            from minio.commonconfig import CopySource
            client.copy_object(
                self.bucket_name,
                dest_name,
                CopySource(self.bucket_name, source_name)
            )
            return True
        except Exception as e:
            logger.error(f"MinIO复制失败: {str(e)}")
            return self._local_copy_fallback(source_name, dest_name)

    # ===== 本地存储回退方法 =====

    def _get_local_base_path(self) -> str:
        """获取本地存储基础路径"""
        return os.environ.get('UPLOAD_FOLDER', 'data/uploads')

    def _get_local_path(self, object_name: str) -> str:
        """获取本地存储路径"""
        return os.path.join(self._get_local_base_path(), object_name)

    def _local_upload_fallback(self, object_name: str, file_path: str) -> dict:
        """本地上传回退"""
        local_path = self._get_local_path(object_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        import shutil
        shutil.copy2(file_path, local_path)
        return {'storage_type': 'local', 'object_name': object_name, 'path': local_path}

    def _local_upload_bytes_fallback(self, object_name: str, data: bytes) -> dict:
        """本地字节上传回退"""
        local_path = self._get_local_path(object_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(data)
        return {'storage_type': 'local', 'object_name': object_name, 'path': local_path}

    def _local_download_fallback(self, object_name: str, file_path: str) -> bool:
        """本地下载回退"""
        local_path = self._get_local_path(object_name)
        if os.path.exists(local_path):
            import shutil
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            shutil.copy2(local_path, file_path)
            return True
        return False

    def _local_download_bytes_fallback(self, object_name: str) -> Optional[bytes]:
        """本地字节下载回退"""
        local_path = self._get_local_path(object_name)
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                return f.read()
        return None

    def _local_delete_fallback(self, object_name: str) -> bool:
        """本地删除回退"""
        local_path = self._get_local_path(object_name)
        if os.path.exists(local_path):
            os.remove(local_path)
            return True
        return False

    def _local_list_fallback(self, prefix: str) -> list:
        """本地列表回退"""
        base = self._get_local_base_path()
        search_dir = os.path.join(base, prefix) if prefix else base
        results = []
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for f in files:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, base)
                    results.append({
                        'object_name': rel_path.replace('\\', '/'),
                        'size': os.path.getsize(full_path),
                        'last_modified': os.path.getmtime(full_path)
                    })
        return results

    def _local_copy_fallback(self, source_name: str, dest_name: str) -> bool:
        """本地复制回退"""
        src = self._get_local_path(source_name)
        dst = self._get_local_path(dest_name)
        if os.path.exists(src):
            import shutil
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            return True
        return False


# 全局单例
_storage = None


def get_storage() -> MinIOStorage:
    """获取全局存储实例"""
    global _storage
    if _storage is None:
        _storage = MinIOStorage()
    return _storage
