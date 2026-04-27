from __future__ import annotations

from augochloropsis_ai.db.models import ModelVersion, Species
from augochloropsis_ai.ml.global_identifier import (
    GlobalIdentificationProbability,
    GlobalIdentificationResult,
)
from augochloropsis_ai.ml.inference_pipeline import InferenceProbability, InferenceResult

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc\xf8\xff"
    b"\x1f\x00\x03\x03\x01\xff\xa5^\xad\x1b\x00\x00\x00\x00IEND\xaeB`\x82"
)


class FakeGlobalIdentifier:
    model_name = "openai/clip-vit-base-patch32"

    def identify_bytes(self, _):
        return GlobalIdentificationResult(
            predicted_code="apis_mellifera",
            predicted_scientific_name="Apis mellifera",
            predicted_common_name="western honey bee",
            confidence=0.84,
            probabilities=[
                GlobalIdentificationProbability(
                    code="apis_mellifera",
                    scientific_name="Apis mellifera",
                    common_name="western honey bee",
                    probability=0.84,
                )
            ],
            model_name=self.model_name,
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


def test_history_lists_specific_and_openai_records(test_client, db_session, monkeypatch):
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
    monkeypatch.setattr(
        "augochloropsis_ai.services.global_identification_service.get_global_identifier",
        lambda: FakeGlobalIdentifier(),
    )

    specific_response = test_client.post(
        "/api/v1/predictions",
        files={"file": ("specific.png", PNG_BYTES, "image/png")},
    )
    assert specific_response.status_code == 201

    openai_response = test_client.post(
        "/api/v1/global-identifications",
        files={"file": ("openai.png", PNG_BYTES, "image/png")},
    )
    assert openai_response.status_code == 201
    assert openai_response.json()["global_identification_id"] == 1

    history_response = test_client.get("/api/v1/history", params={"limit": 10, "offset": 0})
    assert history_response.status_code == 200
    payload = history_response.json()
    assert payload["total"] == 2
    assert {item["source"] for item in payload["items"]} == {"specific", "openai"}

    openai_history_response = test_client.get("/api/v1/history", params={"source": "openai"})
    assert openai_history_response.status_code == 200
    openai_payload = openai_history_response.json()
    assert openai_payload["total"] == 1
    assert openai_payload["items"][0]["source_label"] == "OpenAI"
    assert openai_payload["items"][0]["predicted_scientific_name"] == "Apis mellifera"


def test_history_paginates_records(test_client, db_session, monkeypatch):
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

    for index in range(3):
        response = test_client.post(
            "/api/v1/predictions",
            files={"file": (f"bee-{index}.png", PNG_BYTES, "image/png")},
        )
        assert response.status_code == 201

    first_page = test_client.get("/api/v1/history", params={"limit": 2, "offset": 0})
    assert first_page.status_code == 200
    assert first_page.json()["total"] == 3
    assert len(first_page.json()["items"]) == 2

    second_page = test_client.get("/api/v1/history", params={"limit": 2, "offset": 2})
    assert second_page.status_code == 200
    assert len(second_page.json()["items"]) == 1
