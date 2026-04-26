# Resultados

## Experimento piloto v001

O primeiro dataset baixado do GBIF foi invalidado para apresentação porque a classe
`aug_callichroa` continha imagens de etiquetas de espécime, não imagens úteis da abelha.

## Experimento piloto v002

Dataset corrigido baixado do GBIF com filtro para iNaturalist research-grade observations e
`HUMAN_OBSERVATION`:

- 2 classes do gênero *Augochloropsis*;
- 12 imagens de `aug_metallica`;
- 10 imagens de `aug_ignita`;
- 22 imagens válidas no total;
- encoder `facebook/dinov2-small`;
- classificador MLP supervisionado;
- versão registrada e ativa: `dinov2_small_mlp_demo_v002`.

Métricas no split de teste:

- acurácia: 0.7500;
- precisão ponderada: 0.8333;
- revocação ponderada: 0.7500;
- F1 ponderado: 0.7333.

Validação funcional:

- modelo específico ativo no SQLite;
- endpoint `/api/v1/predictions` testado com upload real;
- identificador global separado em `/api/v1/global-identifications`;
- artefatos exportados em `artifacts/models/dinov2_small_mlp_demo_v002`.

Limitações:

- base piloto muito pequena;
- imagens públicas podem ter características diferentes das imagens reais da pesquisadora;
- resultado ainda não deve ser tratado como desempenho científico final.

Próximos passos:

- substituir ou complementar o piloto com imagens reais validadas;
- aumentar quantidade de exemplares por espécie;
- analisar a matriz de confusão;
- comparar o identificador global com o modelo específico em um conjunto de imagens comum.
