from __future__ import annotations

from augochloropsis_ai.db.models import ModelVersion, Species
from augochloropsis_ai.ml.inference_pipeline import InferenceResult, InferenceProbability


def _seed_species_and_model(db_session):
    species = Species(code="aug_smaragdina", scientific_name="Augochloropsis smaragdina")
    model = ModelVersion(
        version="dinov2_base_mlp_test",
        encoder_name="facebook/dinov2-base",
        classifier_type="mlp",
        artifact_dir="/tmp/non-existent-for-test",
        metrics_json="{}",
        is_active=True,
    )
    db_session.add_all([species, model])
    db_session.commit()


def test_prediction_requires_active_model(test_client):
    response = test_client.post(
        "/api/v1/predictions",
        files={"file": ("bee.png", b"not-really-an-image", "image/png")},
    )
    assert response.status_code == 503


def test_prediction_rejects_invalid_image(test_client, db_session):
    _seed_species_and_model(db_session)
    response = test_client.post(
        "/api/v1/predictions",
        files={"file": ("bee.txt", b"not-really-an-image", "text/plain")},
    )
    assert response.status_code == 400


def test_prediction_creation_flow(test_client, db_session, monkeypatch):
    _seed_species_and_model(db_session)

    def fake_predict_bytes(_, __, ___):
        return InferenceResult(
            predicted_species_code="aug_smaragdina",
            confidence=0.91,
            probabilities=[
                InferenceProbability(species_code="aug_smaragdina", probability=0.91),
            ],
            model_version="dinov2_base_mlp_test",
            inference_ms=42.5,
        )

    monkeypatch.setattr(
        "augochloropsis_ai.ml.inference_pipeline.InferencePipeline.predict_bytes",
        fake_predict_bytes,
    )

    response = test_client.post(
        "/api/v1/predictions",
        files={
            "file": (
                "bee.png",
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc\xf8\xff\x1f\x00\x03\x03\x01\xff\xa5^\xad\x1b\x00\x00\x00\x00IEND\xaeB`\x82",
                "image/png",
            )
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["predicted_species"]["code"] == "aug_smaragdina"
    assert payload["confidence"] == 0.91
    assert payload["probabilities"][0]["species_code"] == "aug_smaragdina"

    history_response = test_client.get("/api/v1/predictions")
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1
