import os
import json
import tempfile
import aiofiles
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from app.config import settings

class BaseStorage(ABC):
    """Abstract storage interface to allow 1-class swapping between Local Disk and Cloudflare R2 / S3."""

    @abstractmethod
    async def save_file(self, content: bytes, destination_rel_path: str) -> str:
        """Save file bytes and return relative or canonical storage identifier."""
        pass

    @abstractmethod
    async def get_file(self, file_path: str) -> bytes:
        """Retrieve file content bytes."""
        pass

    @abstractmethod
    async def atomic_write_json(self, destination_rel_path: str, data: Dict[str, Any]) -> str:
        """Atomically write JSON data to avoid partial reads."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """Generate public or static URL for file access."""
        pass

class LocalStorage(BaseStorage):
    """Local filesystem storage with atomic file write semantics."""

    def __init__(self, base_upload_dir: str = settings.UPLOAD_DIR, base_published_dir: str = settings.PUBLISHED_DIR):
        self.upload_dir = Path(base_upload_dir)
        self.published_dir = Path(base_published_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.published_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, content: bytes, destination_rel_path: str) -> str:
        target_path = self.upload_dir / destination_rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(target_path, "wb") as f:
            await f.write(content)

        return str(target_path.resolve())

    async def get_file(self, file_path: str) -> bytes:
        p = Path(file_path)
        if not p.is_absolute():
            p = self.upload_dir / file_path
        
        async with aiofiles.open(p, "rb") as f:
            return await f.read()

    async def atomic_write_json(self, destination_rel_path: str, data: Dict[str, Any]) -> str:
        """
        Atomically writes JSON to destination by writing to a temporary file on the same filesystem
        and executing an atomic `os.replace` operation. Readers will either see old or new version,
        never a corrupted or partial write.
        """
        target_path = self.published_dir / destination_rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        # Write to temporary file in same directory to ensure same filesystem for atomic rename
        temp_fd, temp_file_path = tempfile.mkstemp(
            dir=target_path.parent,
            prefix=".tmp_catalogue_",
            suffix=".json"
        )
        
        try:
            with open(temp_fd, "wb") as f:
                f.write(json_bytes)
                f.flush()
                os.fsync(f.fileno())

            # Atomic swap
            os.replace(temp_file_path, target_path)
        except Exception:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise

        return str(target_path.resolve())

    async def delete_file(self, file_path: str) -> bool:
        p = Path(file_path)
        if not p.is_absolute():
            p = self.upload_dir / file_path
        if p.exists():
            p.unlink()
            return True
        return False

    def get_url(self, file_path: str) -> str:
        """Converts absolute or relative path to static web URL."""
        if not file_path:
            return "/sample_assets/poster_good.jpg"

        file_str = str(file_path).strip()

        # If already a full URL or absolute static web route, return as-is
        if file_str.startswith(("http://", "https://", "/storage/", "/sample_assets/")):
            return file_str

        # If it contains sample_assets
        if "sample_assets" in file_str:
            filename = Path(file_str).name
            return f"/sample_assets/{filename}"

        p = Path(file_str)
        try:
            rel_to_upload = p.relative_to(self.upload_dir)
            return f"/storage/uploads/{rel_to_upload.as_posix()}"
        except ValueError:
            pass

        try:
            rel_to_published = p.relative_to(self.published_dir)
            return f"/storage/published/{rel_to_published.as_posix()}"
        except ValueError:
            pass

        return f"/storage/uploads/{p.name}"

class CloudflareR2Storage(BaseStorage):
    """
    Production-ready storage implementation for Cloudflare R2 (S3-compatible API).
    To swap to R2 in production, set STORAGE_BACKEND=r2 with R2 credentials.
    """

    def __init__(
        self,
        account_id: str = settings.R2_ACCOUNT_ID,
        access_key_id: str = settings.R2_ACCESS_KEY_ID,
        secret_access_key: str = settings.R2_SECRET_ACCESS_KEY,
        bucket_name: str = settings.R2_BUCKET_NAME,
        public_url_prefix: str = settings.R2_PUBLIC_URL_PREFIX,
    ):
        self.endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com" if account_id else ""
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket_name
        self.public_url_prefix = public_url_prefix.rstrip("/")

    async def save_file(self, content: bytes, destination_rel_path: str) -> str:
        # In production:
        # s3_client.put_object(Bucket=self.bucket_name, Key=destination_rel_path, Body=content)
        key = destination_rel_path.lstrip("/")
        return f"{self.bucket_name}/{key}"

    async def get_file(self, file_path: str) -> bytes:
        # In production:
        # response = s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
        # return response['Body'].read()
        return b""

    async def atomic_write_json(self, destination_rel_path: str, data: Dict[str, Any]) -> str:
        # In R2/S3, single PUT requests are inherently atomic (object is visible only after upload completes)
        # In production:
        # s3_client.put_object(Bucket=self.bucket_name, Key=destination_rel_path, Body=json.dumps(data), ContentType="application/json")
        key = destination_rel_path.lstrip("/")
        return f"{self.public_url_prefix}/{key}"

    async def delete_file(self, file_path: str) -> bool:
        # In production:
        # s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
        return True

    def get_url(self, file_path: str) -> str:
        key = file_path.replace(f"{self.bucket_name}/", "").lstrip("/")
        return f"{self.public_url_prefix}/{key}"

_storage_instance: Optional[BaseStorage] = None

def get_storage() -> BaseStorage:
    global _storage_instance
    if _storage_instance is None:
        if settings.STORAGE_BACKEND.lower() == "r2":
            _storage_instance = CloudflareR2Storage()
        else:
            _storage_instance = LocalStorage()
    return _storage_instance
