from __future__ import annotations

from datetime import UTC, datetime

from fastapi import UploadFile

from augochloropsis_ai.core.config import Settings, get_settings
from augochloropsis_ai.ml.global_identifier import ClipGlobalIdentifier, get_global_identifier
from augochloropsis_ai.schemas.global_identification import (
    GlobalIdentificationProbability,
    GlobalIdentificationResponse,
)
from augochloropsis_ai.services.storage_service import StorageService


class GlobalIdentificationService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        storage_service: StorageService | None = None,
        identifier: ClipGlobalIdentifier | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.storage_service = storage_service or StorageService(self.settings)
        self.identifier = identifier or get_global_identifier()

    async def identify(self, upload_file: UploadFile) -> GlobalIdentificationResponse:
        stored_upload = await self.storage_service.store_upload(upload_file)
        result = self.identifier.identify_bytes(stored_upload.content)

        return GlobalIdentificationResponse(
            image_url=f"{self.settings.uploads_mount_path}/{stored_upload.relative_path}",
            predicted_code=result.predicted_code,
            predicted_scientific_name=result.predicted_scientific_name,
            predicted_common_name=result.predicted_common_name,
            confidence=result.confidence,
            probabilities=[
                GlobalIdentificationProbability(
                    code=item.code,
                    scientific_name=item.scientific_name,
                    common_name=item.common_name,
                    probability=item.probability,
                )
                for item in result.probabilities
            ],
            model_name=result.model_name,
            created_at=datetime.now(UTC),
            note=(
                "Baseline global zero-shot. Use como comparacao ampla; "
                "o modelo especifico do projeto continua separado."
            ),
        )
