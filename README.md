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
- Dois caminhos de identificação separados:
  - identificador global/pretreinado para comparação ampla;
  - modelo específico do projeto com encoder DINOv2 frozen + classificador MLP.
- Exibição de confiança e probabilidades por classe.
- Histórico de resultados persistido em SQLite para o modelo específico.
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

Para um primeiro piloto rápido com imagens públicas do GBIF:

```bash
cd backend
source ../.venv/bin/activate
python scripts/download_gbif_demo_dataset.py --images-per-species 12
python scripts/seed_species.py --csv ../data/raw/metadata/species_seed.demo.csv
```

Depois treine e registre o modelo específico:

```bash
cd backend
source ../.venv/bin/activate
python scripts/run_training_pipeline.py \
  --raw-catalog ../data/raw/metadata/raw_catalog.csv \
  --clean-catalog ../data/interim/metadata/clean_catalog.csv \
  --split-manifest ../data/processed/metadata/split_manifest.csv \
  --encoder-name facebook/dinov2-small \
  --version dinov2_small_mlp_demo_v002
```

## Observações

- O MVP assume uma imagem por requisição.
- O banco armazena metadados e caminhos de arquivo; as imagens ficam no filesystem.
- O treino roda offline por CLI; a API apenas consome artefatos versionados.
- O identificador global é um baseline separado e não substitui o modelo específico treinado para o projeto.
