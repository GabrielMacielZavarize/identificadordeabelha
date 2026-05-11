from __future__ import annotations

from sqlalchemy.orm import Session

from beeai.core.config import Settings, get_settings
from beeai.db.models import GlobalIdentification, Prediction
from beeai.repositories.global_identification_repository import (
    GlobalIdentificationRepository,
)
from beeai.repositories.prediction_repository import PredictionRepository
from beeai.schemas.history import (
    HistorySourceFilter,
    IdentificationHistoryItem,
    IdentificationHistoryPage,
)


class HistoryService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        prediction_repository: PredictionRepository | None = None,
        global_repository: GlobalIdentificationRepository | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.prediction_repository = prediction_repository or PredictionRepository()
        self.global_repository = global_repository or GlobalIdentificationRepository()

    def list_history(
        self,
        db: Session,
        *,
        source: HistorySourceFilter = "all",
        limit: int = 10,
        offset: int = 0,
    ) -> IdentificationHistoryPage:
        items: list[IdentificationHistoryItem] = []
        total = 0
        fetch_limit = offset + limit

        if source in ("all", "specific"):
            total += self.prediction_repository.count_predictions(db)
            predictions = self.prediction_repository.list_predictions(db, limit=fetch_limit)
            items.extend(self._prediction_to_item(prediction) for prediction in predictions)

        if source in ("all", "openai"):
            total += self.global_repository.count_global_identifications(db)
            identifications = self.global_repository.list_global_identifications(
                db,
                limit=fetch_limit,
            )
            items.extend(
                self._global_identification_to_item(identification)
                for identification in identifications
            )

        items.sort(key=lambda item: (item.created_at, item.item_id), reverse=True)
        return IdentificationHistoryPage(
            items=items[offset : offset + limit],
            total=total,
            limit=limit,
            offset=offset,
        )

    def _prediction_to_item(self, prediction: Prediction) -> IdentificationHistoryItem:
        return IdentificationHistoryItem(
            item_id=prediction.id,
            source="specific",
            source_label="Modelo treinado",
            image_url=f"{self.settings.uploads_mount_path}/{prediction.stored_path}",
            predicted_code=prediction.predicted_species.code,
            predicted_scientific_name=prediction.predicted_species.scientific_name,
            confidence=prediction.confidence,
            model_name=prediction.model_version.version,
            inference_ms=prediction.inference_ms,
            created_at=prediction.created_at,
        )

    def _global_identification_to_item(
        self,
        identification: GlobalIdentification,
    ) -> IdentificationHistoryItem:
        return IdentificationHistoryItem(
            item_id=identification.id,
            source="openai",
            source_label="OpenAI",
            image_url=f"{self.settings.uploads_mount_path}/{identification.stored_path}",
            predicted_code=identification.predicted_code,
            predicted_scientific_name=identification.predicted_scientific_name,
            predicted_common_name=identification.predicted_common_name,
            confidence=identification.confidence,
            model_name=identification.model_name,
            inference_ms=identification.inference_ms,
            created_at=identification.created_at,
        )
