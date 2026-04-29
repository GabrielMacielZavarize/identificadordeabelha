# Experimentos

Registre aqui cada execução relevante do pipeline:

| versão | encoder | hidden_dims | dataset | accuracy | observações |
|---|---|---|---|---|---|
| global_clip_zero_shot | openai/clip-vit-base-patch32 | n/a | labels globais fixos | n/a | baseline global separado, sem treino local |
| dinov2_small_mlp_demo_v001 | facebook/dinov2-small | [256,128] | GBIF piloto, 36 imagens, 3 classes | 0.6667 | inválido para apresentação: classe `aug_callichroa` continha imagens de etiquetas |
| dinov2_small_mlp_demo_v002 | facebook/dinov2-small | [256,128] | GBIF/iNaturalist filtrado, 22 imagens, 2 classes | 0.7500 | modelo específico corrigido e ativo |
| dinov3_vits16_mlp_test_v001 | facebook/dinov3-vits16-pretrain-lvd1689m | [256,128] | mesmo dataset filtrado do DINOv2 | 0.5000 | versão experimental registrada; abaixo do DINOv2 no piloto atual |
