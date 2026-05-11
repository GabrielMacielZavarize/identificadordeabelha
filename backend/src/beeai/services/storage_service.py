from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from beeai.core.config import Settings, get_settings
from beeai.core.exceptions import InvalidRequestError


@dataclass(slots=True)
class StoredUpload:
    original_filename: str
    relative_path: str
    sha256: str
    content: bytes


class StorageService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def store_upload(self, upload_file: UploadFile) -> StoredUpload:
        original_filename = upload_file.filename or "uploaded_image"
        suffix = Path(original_filename).suffix.lower()
        if suffix not in self.settings.allowed_image_extensions:
            raise InvalidRequestError("Unsupported file extension. Only JPG and PNG are accepted.")

        if upload_file.content_type not in self.settings.allowed_mime_types:
            raise InvalidRequestError("Unsupported MIME type. Only image/jpeg and image/png are accepted.")

        content = await upload_file.read()
        if not content:
            raise InvalidRequestError("Uploaded file is empty.")

        if len(content) > self.settings.max_upload_size_bytes:
            raise InvalidRequestError("Uploaded file exceeds the configured size limit.")

        relative_dir = Path(datetime.now(UTC).strftime("%Y/%m/%d"))
        relative_path = relative_dir / f"{uuid4().hex}{suffix}"
        absolute_path = self.settings.upload_dir / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)

        return StoredUpload(
            original_filename=original_filename,
            relative_path=relative_path.as_posix(),
            sha256=hashlib.sha256(content).hexdigest(),
            content=content,
        )
