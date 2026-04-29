# Identificador de Abelhas

Monorepo acadêmico para classificação de espécies do gênero *Augochloropsis* a partir de imagens digitais. O projeto combina uma API FastAPI, uma interface React e um pipeline offline de visão computacional para gerar artefatos de modelo versionados.

## O que o sistema faz

- Recebe upload de imagens JPG/PNG pela interface web.
- Executa dois fluxos de identificação separados:
  - modelo específico do projeto: DINOv2 frozen + classificador MLP treinado com as classes cadastradas;
  - identificador global: baseline zero-shot com CLIP para comparação ampla.
- Exibe espécie prevista, confiança e probabilidades por classe.
- Persiste histórico de predições no SQLite.
- Mantém CRUD simples de espécies.
- Armazena uploads no filesystem e artefatos treinados em `artifacts/models`.

## Estrutura

- `backend/`: API FastAPI, SQLite, serviços de upload, inferência e pipeline offline.
- `frontend/`: aplicação React/Vite para upload, resultado, histórico e espécies.
- `data/`: datasets, banco SQLite local, uploads e arquivos intermediários.
- `artifacts/`: versões empacotadas dos modelos treinados.
- `docs/`: requisitos, arquitetura, metodologia, experimentos e resultados.
- `notebooks/`: análise exploratória e análise de erros.

## Rodando com Docker

Use Docker quando quiser iniciar backend e frontend juntos, sem manter dois terminais configurados manualmente.

Se o modelo ativo for DINOv3, informe um token Hugging Face com acesso ao repositório gated da Meta. O login feito no host com `hf auth login` não entra automaticamente no container:

```bash
export HF_TOKEN=hf_seu_token_read_aqui
```

Também pode copiar `.env.example` para `.env` e preencher `HF_TOKEN` ali. Não commite esse arquivo.

```bash
docker compose up --build
```

O primeiro build pode demorar porque instala PyTorch, Transformers e dependências de visão computacional no container do backend. A primeira inferência com DINOv3 também pode demorar porque o container baixa os pesos do Hugging Face; o cache fica persistido em um volume Docker.

Depois acesse:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8001`
- Health check: `http://localhost:8001/api/v1/health`

O Compose sobe dois serviços separados:

- `backend`: FastAPI exposto em `localhost:8001`, com SQLite em `data/db/app.sqlite3`;
- `frontend`: Vite em `:5173`, usando proxy interno para falar com o backend.

Os diretórios `data/` e `artifacts/` são montados como volumes bind no backend. Assim, uploads, banco local e modelos treinados continuam disponíveis após recriar os containers.

A imagem Docker do backend instala o conjunto de runtime para API e inferência. O pipeline de treino/análise continua recomendado no ambiente local do backend, porque inclui dependências extras como pandas, scikit-learn, matplotlib e seaborn.

Para parar:

```bash
docker compose down
```

## Rodando localmente

### Backend

Instalação inicial:

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -e ".[dev]"
```

Inicialização do backend no dia a dia:

```bash
cd backend
source ../.venv/bin/activate
uvicorn augochloropsis_ai.api.main:app --reload --app-dir src
```

A API cria os diretórios de runtime e inicializa o SQLite automaticamente ao subir. Se quiser inicializar o banco manualmente:

```bash
cd backend
source ../.venv/bin/activate
python scripts/init_db.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Por padrão, o Vite usa proxy para `http://localhost:8000`, então o frontend pode chamar `/api/v1` e `/uploads` sem configurar `VITE_API_BASE_URL`.

## Modelos DINO treinados

O experimento piloto atual usa:

- encoder: `facebook/dinov2-small`;
- classificador: MLP supervisionado;
- versão ativa documentada: `dinov2_small_mlp_demo_v002`;
- dataset piloto: imagens públicas filtradas de GBIF/iNaturalist.

Esse modelo é o resultado principal do projeto. O identificador global com CLIP é apenas um baseline comparativo e não substitui o modelo específico treinado para *Augochloropsis*.

O frontend lista as versões registradas em `/api/v1/models`. Assim, versões DINOv2 e DINOv3 podem ficar disponíveis no mesmo seletor para comparação, desde que seus artefatos tenham sido treinados e registrados pelo pipeline.

## Pipeline offline de treino

Para baixar um dataset piloto público e semear espécies:

```bash
cd backend
source ../.venv/bin/activate
python scripts/download_gbif_demo_dataset.py --images-per-species 12
python scripts/seed_species.py --csv ../data/raw/metadata/species_seed.demo.csv
```

Depois, para treinar, avaliar, empacotar e registrar o modelo específico:

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

Para criar uma versão experimental com DINOv3 e comparar contra o DINOv2:

1. Acesse a página do modelo no Hugging Face, aceite os termos da licença e autentique a máquina:

```bash
huggingface-cli login
```

Também é possível exportar um token com acesso ao modelo:

```bash
export HF_TOKEN=<seu-token>
```

2. Execute o pipeline:

```bash
cd backend
source ../.venv/bin/activate
python scripts/run_training_pipeline.py \
  --raw-catalog ../data/raw/metadata/raw_catalog.csv \
  --clean-catalog ../data/interim/metadata/clean_catalog.csv \
  --split-manifest ../data/processed/metadata/split_manifest.csv \
  --embeddings-dir ../data/interim/embeddings/dinov3_vits16_mlp_test_v001 \
  --encoder-name facebook/dinov3-vits16-pretrain-lvd1689m \
  --version dinov3_vits16_mlp_test_v001
```

O DINOv3 requer `transformers>=4.56`. A primeira execução baixa os pesos do Hugging Face, então precisa de internet, acesso concedido ao repositório gated da Meta e pode demorar.

## Testes e qualidade

Backend:

```bash
cd backend
source ../.venv/bin/activate
pytest
ruff check .
mypy src
```

Frontend:

```bash
cd frontend
npm run test
npm run lint
npm run build
```

## Observações

- O MVP assume uma imagem por requisição.
- O backend aceita JPG/JPEG/PNG e limita uploads a 15 MB por padrão.
- O treino roda offline por CLI; a API apenas consome os artefatos registrados.
- A base piloto é pequena e ainda não deve ser tratada como desempenho científico final.
