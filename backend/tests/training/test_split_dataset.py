from __future__ import annotations

import pandas as pd

from augochloropsis_ai.training.split_dataset import assign_split_labels


def test_assign_split_labels_keeps_specimens_together():
    dataframe = pd.DataFrame(
        [
            {"image_id": "1", "specimen_id": "s1", "species_code": "aug_a", "file_path": "/tmp/1.jpg"},
            {"image_id": "2", "specimen_id": "s1", "species_code": "aug_a", "file_path": "/tmp/2.jpg"},
            {"image_id": "3", "specimen_id": "s2", "species_code": "aug_a", "file_path": "/tmp/3.jpg"},
            {"image_id": "4", "specimen_id": "s3", "species_code": "aug_b", "file_path": "/tmp/4.jpg"},
            {"image_id": "5", "specimen_id": "s4", "species_code": "aug_b", "file_path": "/tmp/5.jpg"},
            {"image_id": "6", "specimen_id": "s5", "species_code": "aug_b", "file_path": "/tmp/6.jpg"},
        ]
    )

    split_manifest = assign_split_labels(dataframe, seed=7)
    specimen_split_counts = split_manifest.groupby("specimen_id")["split"].nunique().to_dict()

    assert all(value == 1 for value in specimen_split_counts.values())
