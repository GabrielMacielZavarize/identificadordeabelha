from __future__ import annotations


def test_species_crud_flow(test_client):
    create_response = test_client.post(
        "/api/v1/species",
        json={
            "code": "aug_metallica",
            "scientific_name": "Augochloropsis metallica",
            "description": "Specimen from curated test seed.",
        },
    )
    assert create_response.status_code == 201
    species_id = create_response.json()["id"]

    list_response = test_client.get("/api/v1/species")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    duplicate_response = test_client.post(
        "/api/v1/species",
        json={
            "code": "aug_metallica",
            "scientific_name": "Augochloropsis metallica",
            "description": None,
        },
    )
    assert duplicate_response.status_code == 409

    update_response = test_client.put(
        f"/api/v1/species/{species_id}",
        json={"description": "Updated description."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated description."

    delete_response = test_client.delete(f"/api/v1/species/{species_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False
