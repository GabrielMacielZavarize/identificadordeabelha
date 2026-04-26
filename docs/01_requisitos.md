# Requisitos

## Funcionais

- RF01. Upload de imagem via interface web.
- RF02. Pré-processamento compatível com DINOv2.
- RF03. Extração de embeddings visuais frozen.
- RF04. Classificação multiclasse via MLP supervisionado.
- RF05. Exibição de confiança e probabilidades por classe.
- RF06. Consulta ao histórico de inferências.
- RF07. Persistência de imagem, predição, confiança e timestamp.
- RF08. CRUD simples de espécies do gênero alvo.

## Não funcionais

- RNF01. Execução local em Linux.
- RNF02. Desempenho aceitável em CPU.
- RNF03. Rastreabilidade da inferência.
- RNF04. Código modular e testável.
- RNF05. MVP sem dependência de serviços cloud.
