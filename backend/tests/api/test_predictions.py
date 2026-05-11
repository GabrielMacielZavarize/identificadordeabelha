from __future__ import annotations

from beeai.db.models import ModelVersion, Species
from beeai.ml.inference_pipeline import InferenceProbability, InferenceResult

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0bIDATx\x9cc\xf8\xff\x1f\x00\x03\x03\x01"
    b"\xff\xa5^\xad\x1b\x00\x00\x00\x00IEND\xaeB`\x82"
)


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


def _seed_dinov3_model(db_session):
    model = ModelVersion(
        version="dinov3_vits16_mlp_test",
        encoder_name="facebook/dinov3-vits16-pretrain-lvd1689m",
        classifier_type="mlp",
        artifact_dir="/tmp/non-existent-for-test",
        metrics_json="{}",
        is_active=False,
    )
    db_session.add(model)
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
        "beeai.ml.inference_pipeline.InferencePipeline.predict_bytes",
        fake_predict_bytes,
    )

    response = test_client.post(
        "/api/v1/predictions",
        files={
            "file": (
                "bee.png",
                PNG_BYTES,
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


def test_prediction_can_use_requested_model_version(test_client, db_session, monkeypatch):
    _seed_species_and_model(db_session)
    _seed_dinov3_model(db_session)
    used_versions: list[str] = []

    def fake_predict_bytes(_, __, model_version):
        used_versions.append(model_version.version)
        return InferenceResult(
            predicted_species_code="aug_smaragdina",
            confidence=0.88,
            probabilities=[
                InferenceProbability(species_code="aug_smaragdina", probability=0.88),
            ],
            model_version=model_version.version,
            inference_ms=51.0,
        )

    monkeypatch.setattr(
        "beeai.ml.inference_pipeline.InferencePipeline.predict_bytes",
        fake_predict_bytes,
    )

    response = test_client.post(
        "/api/v1/predictions",
        params={"model_version": "dinov3_vits16_mlp_test"},
        files={
            "file": (
                "bee.png",
                PNG_BYTES,
                "image/png",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert used_versions == ["dinov3_vits16_mlp_test"]
    assert payload["model_version"]["version"] == "dinov3_vits16_mlp_test"
    assert payload["model_version"]["encoder_name"] == "facebook/dinov3-vits16-pretrain-lvd1689m"


def test_prediction_returns_503_when_encoder_requires_access(test_client, db_session, monkeypatch):
    _seed_species_and_model(db_session)

    def fake_predict_bytes(_, __, ___):
        raise RuntimeError("This encoder requires Hugging Face access.")

    monkeypatch.setattr(
        "beeai.ml.inference_pipeline.InferencePipeline.predict_bytes",
        fake_predict_bytes,
    )

    response = test_client.post(
        "/api/v1/predictions",
        files={"file": ("bee.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 503
    assert "Hugging Face access" in response.json()["detail"]


def test_prediction_rejects_unknown_model_version(test_client, db_session):
    _seed_species_and_model(db_session)

    response = test_client.post(
        "/api/v1/predictions",
        params={"model_version": "dinov3_missing"},
        files={"file": ("bee.png", b"not-really-an-image", "image/png")},
    )

    assert response.status_code == 404


def test_model_versions_are_listed_with_active_first(test_client, db_session):
    _seed_species_and_model(db_session)
    _seed_dinov3_model(db_session)

    response = test_client.get("/api/v1/models")

    assert response.status_code == 200
    payload = response.json()
    assert [item["version"] for item in payload] == [
        "dinov2_base_mlp_test",
        "dinov3_vits16_mlp_test",
    ]
