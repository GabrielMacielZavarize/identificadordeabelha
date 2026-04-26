# CRISP-DM

## Business Understanding

- Apoiar a pesquisadora na identificação morfológica de *Augochloropsis*.

## Data Understanding

- Catalogar imagens, exemplares, vistas anatômicas e qualidade de rótulo.

## Data Preparation

- Limpeza do catálogo.
- Split por exemplar para evitar vazamento.
- Extração cacheada de embeddings.

## Modeling

- Encoder visual DINOv2 frozen.
- Classificador MLP supervisionado.

## Evaluation

- Acurácia, precisão, revocação, F1 e matriz de confusão.

## Deployment

- MVP local com FastAPI, React e SQLite.
