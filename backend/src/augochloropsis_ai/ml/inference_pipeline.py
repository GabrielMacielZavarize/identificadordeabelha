from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from augochloropsis_ai.db.models import ModelVersion
from augochloropsis_ai.ml.artifact_loader import ArtifactLoader
from augochloropsis_ai.ml.classifier import predict_probabilities
from augochloropsis_ai.ml.embedder import get_embedder


@dataclass(slots=True)
class InferenceProbability:
    species_code: str
    probability: float


@dataclass(slots=True)
class InferenceResult:
    predicted_species_code: str
    confidence: float
    probabilities: list[InferenceProbability]
    model_version: str
    inference_ms: float


class InferencePipeline:
    def __init__(self, artifact_loader: ArtifactLoader | None = None) -> None:
        self.artifact_loader = artifact_loader or ArtifactLoader()

    def predict_bytes(self, content: bytes, model_version: ModelVersion) -> InferenceResult:
        started_at = perf_counter()
        artifacts = self.artifact_loader.load(model_version)
        embedder = get_embedder(artifacts.encoder_name)
        embedding = embedder.embed_bytes(content)
        probabilities = predict_probabilities(artifacts.classifier, embedding)

        ordered = sorted(
            [
                InferenceProbability(
                    species_code=artifacts.label_map[index],
                    probability=float(probability),
                )
                for index, probability in enumerate(probabilities)
            ],
            key=lambda item: item.probability,
            reverse=True,
        )
        top_prediction = ordered[0]
        inference_ms = (perf_counter() - started_at) * 1000

        return InferenceResult(
            predicted_species_code=top_prediction.species_code,
            confidence=top_prediction.probability,
            probabilities=ordered,
            model_version=artifacts.version,
            inference_ms=inference_ms,
        )
