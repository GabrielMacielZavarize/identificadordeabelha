# Artifacts

Diretório reservado para artefatos versionados de modelos treinados.

Estrutura esperada:

```text
artifacts/models/<version>/
├── classifier_state.pt
├── label_map.json
├── training_config.yaml
├── metrics.json
└── confusion_matrix.png
```

Nenhum modelo é versionado automaticamente no repositório. O diretório é preenchido pelo pipeline offline de treino.
