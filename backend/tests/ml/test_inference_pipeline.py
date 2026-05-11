from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from beeai.ml.artifact_loader import LoadedArtifacts
from beeai.ml.inference_pipeline import InferencePipeline


def test_inference_pipeline_orders_probabilities(monkeypatch):
    class FakeLoader:
        def load(self, _):
            return LoadedArtifacts(
                version="dinov2_base_mlp_test",
                encoder_name="facebook/dinov2-base",
                classifier_type="mlp",
                label_map={0: "aug_a", 1: "aug_b"},
                classifier=object(),
                config={},
                metrics={},
            )

    class FakeEmbedder:
        def embed_bytes(self, _):
            return np.asarray([0.1, 0.2, 0.3], dtype=np.float32)

    monkeypatch.setattr(
        "beeai.ml.inference_pipeline.get_embedder",
        lambda _model_name: FakeEmbedder(),
    )
    monkeypatch.setattr(
        "beeai.ml.inference_pipeline.predict_probabilities",
        lambda _classifier, _embedding: np.asarray([0.2, 0.8], dtype=np.float32),
    )

    pipeline = InferencePipeline(artifact_loader=FakeLoader())
    result = pipeline.predict_bytes(
        b"fake-image-content",
        SimpleNamespace(version="dinov2_base_mlp_test"),
    )

    assert result.predicted_species_code == "aug_b"
    assert result.probabilities[0].species_code == "aug_b"
    assert abs(sum(item.probability for item in result.probabilities) - 1.0) < 1e-6
