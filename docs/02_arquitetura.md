# Arquitetura

## Visão geral

- `frontend/`: interface React para upload, histórico e cadastro de espécies.
- `backend/`: FastAPI, regras de negócio, SQLite e acesso a artefatos.
- `data/`: datasets, uploads e banco do MVP.
- `artifacts/`: versões exportadas do classificador treinado.

## Fluxo principal

1. Upload de imagem no frontend.
2. Validação e persistência do arquivo no backend.
3. Carregamento do modelo ativo.
4. Extração de embedding com DINOv2 frozen.
5. Classificação com MLP treinado.
6. Persistência do resultado no SQLite.
7. Retorno de espécie prevista, confiança e probabilidades.
