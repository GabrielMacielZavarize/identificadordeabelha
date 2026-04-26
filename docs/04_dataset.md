# Dataset

## Catálogos

- `data/raw/metadata/raw_catalog.csv`: inventário bruto.
- `data/interim/metadata/clean_catalog.csv`: base limpa e validada.
- `data/processed/metadata/split_manifest.csv`: split final com `train`, `val` e `test`.

## Convenções

- `species_code`: identificador estável da espécie.
- `specimen_id`: agrupador para impedir vazamento entre splits.
- `view_type`: dorsal, lateral, frontal, asa ou equivalente.
- `label_status`: `validated`, `pending` ou `discarded`.
