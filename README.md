# Identificador de Abelhas

Monorepo do projeto acadêmico de classificação de espécies do gênero *Augochloropsis* a partir de imagens digitais.

## Estrutura

- `backend/`: API FastAPI, persistência SQLite e pipeline de IA.
- `frontend/`: interface React para upload, histórico e cadastro de espécies.
- `data/`: datasets, uploads e banco local.
- `artifacts/`: modelos treinados e métricas exportadas.
- `docs/`: requisitos, arquitetura, metodologia e resultados.
- `notebooks/`: análise exploratória e análise de erros.

## MVP

- Upload de imagem via interface web.
- Inferência de espécie com encoder DINOv2 frozen + classificador MLP.
- Exibição de confiança e probabilidades por classe.
- Histórico de resultados persistido em SQLite.
- CRUD simples de espécies.

## Backend

```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -e ".[dev]"
python scripts/init_db.py
uvicorn augochloropsis_ai.api.main:app --reload --app-dir src
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Pipeline offline de treino

```bash
cd backend
source ../.venv/bin/activate
python scripts/run_training_pipeline.py \
  --raw-catalog ../data/raw/metadata/raw_catalog.csv \
  --clean-catalog ../data/interim/metadata/clean_catalog.csv \
  --split-manifest ../data/processed/metadata/split_manifest.csv
```

## Observações

- O MVP assume uma imagem por requisição.
- O banco armazena metadados e caminhos de arquivo; as imagens ficam no filesystem.
- O treino roda offline por CLI; a API apenas consome artefatos versionados.
