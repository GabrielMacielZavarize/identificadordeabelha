# BeeAI — Guia de Treino no Kaggle

Este guia documenta o processo completo de treino do modelo BeeAI usando o Kaggle (GPU gratuita), incluindo erros encontrados e suas soluções.

---

## Por que Kaggle?

- GPU T4 (15 GB VRAM) gratuita — 30 horas por semana
- Sem cartão de crédito
- Suporte completo a PyTorch, HuggingFace Transformers e DINOv2
- Sessões de até 9 horas (suficiente para qualquer treino do BeeAI)
- Outputs persistidos após a sessão — arquivos ficam disponíveis para download

---

## Pré-requisitos

- Conta no GitHub com o repositório `identificadordeabelha`
- Personal Access Token do GitHub (se o repositório for privado)
- Conta no Kaggle com telefone verificado

---

## Setup inicial (uma vez só)

### 1. Criar conta no Kaggle

Acesse [kaggle.com](https://kaggle.com) e crie uma conta.

### 2. Verificar telefone (obrigatório para GPU)

Sem verificação de telefone, a opção de GPU aparece como `None` e não pode ser selecionada.

**Kaggle → Settings → Phone Verification → Verify**

### 3. Criar Personal Access Token no GitHub

Necessário apenas se o repositório for privado.

1. GitHub → clique na foto de perfil → **Settings**
2. No menu esquerdo (final da página): **Developer settings**
3. **Personal access tokens → Tokens (classic)**
4. **Generate new token (classic)**
5. Selecione a permissão `repo` → validade 90 dias → **Generate token**
6. Copie o token (aparece apenas uma vez)

### 4. Adicionar o token como secret no Kaggle

Secrets no Kaggle são adicionados **de dentro de um notebook**, não no Settings global.

1. Crie ou abra um notebook
2. No menu superior: **Add-ons → Secrets → Add new secret**
   - Name: `GITHUB_TOKEN`
   - Value: o token copiado acima
3. Salve

---

## Importar o notebook

1. Acesse [kaggle.com/code](https://kaggle.com/code) → **New Notebook**
2. **File → Import Notebook** → selecione `notebooks/04_kaggle_training.ipynb`
3. Após importar, vá em **Settings (painel direito) → Accelerator → GPU T4**
4. Ative também: **Settings → Internet → On** (obrigatório para clonar o GitHub)

---

## O que alterar a cada novo treino

Abra a **Célula 2** do notebook e ajuste os parâmetros conforme a tabela abaixo:

```python
# Célula 2 — edite antes de executar

GITHUB_REPO_URL    = "https://github.com/GabrielMacielZavarize/identificadordeabelha"
MODEL_VERSION      = "dinov2_small_mlp_v001"   # ← altere aqui
ENCODER_NAME       = "facebook/dinov2-small"    # ← altere aqui
IMAGES_PER_SPECIES = 150                         # ← altere aqui
```

| Parâmetro | Quando alterar | Exemplos |
|---|---|---|
| `MODEL_VERSION` | Sempre — cada treino precisa de um nome único | `dinov2_base_mlp_v001`, `dinov3_vitl16_mlp_v001` |
| `ENCODER_NAME` | Quando quiser testar um encoder diferente | ver tabela abaixo |
| `IMAGES_PER_SPECIES` | Quando quiser mais dados ou treino mais rápido | 50 (demo), 150 (padrão), 300+ (produção) |

> **Convenção de nome:** `{encoder}_{classificador}_{versao}` — ex: `dinov2_base_mlp_v002`, `dinov3_vitl16_mlp_v001`

---

## Encoders disponíveis no Kaggle

O pipeline suporta qualquer encoder compatível com `AutoModel` + `AutoImageProcessor` do HuggingFace Transformers. As famílias abaixo foram testadas ou verificadas como compatíveis.

---

### DINOv2 — Meta AI (público, sem token)

Todos funcionam no Kaggle sem configuração adicional.

| Model ID | Params | Dim | VRAM | Quando usar |
|---|---|---|---|---|
| `facebook/dinov2-small` | 22M | 384 | ~1 GB | Iterações rápidas, demos |
| `facebook/dinov2-base` | 86M | 768 | ~2 GB | Boa qualidade com custo moderado |
| `facebook/dinov2-large` | 300M | 1024 | ~5 GB | Alta qualidade — recomendado para producao |
| `facebook/dinov2-giant` | 1B | 1536 | ~10 GB | Máxima qualidade DINOv2, cabe na T4 |
| `facebook/dinov2-with-registers-small` | 22M | 384 | ~1 GB | Versão melhorada do small (register tokens) |
| `facebook/dinov2-with-registers-base` | 86M | 768 | ~2 GB | Versão melhorada do base |
| `facebook/dinov2-with-registers-large` | 300M | 1024 | ~5 GB | Melhor DINOv2 público disponível |
| `facebook/dinov2-with-registers-giant` | 1B | 1536 | ~10 GB | Máximo DINOv2 com registers |

> Os modelos `with-registers` usam register tokens (mesma técnica do DINOv3) e geralmente produzem features mais limpas. Preferir estes sobre as variantes sem registers.

---

### DINOv3 ViT — Meta AI (gated, requer HF_TOKEN)

Requer aceitar os termos de licença na página do modelo no HuggingFace e autenticar com `HF_TOKEN`.

| Model ID | Params | Dim | VRAM | Quando usar |
|---|---|---|---|---|
| `facebook/dinov3-vits16-pretrain-lvd1689m` | 21M | 384 | ~1 GB | DINOv3 mais leve, iterações rápidas |
| `facebook/dinov3-vits16plus-pretrain-lvd1689m` | 29M | 384 | ~1 GB | ViT-S com SwiGLU (ligeiramente melhor) |
| `facebook/dinov3-vitb16-pretrain-lvd1689m` | 86M | 768 | ~2 GB | Boa relação qualidade/velocidade |
| `facebook/dinov3-vitl16-pretrain-lvd1689m` | 300M | 1024 | ~5 GB | Melhor opção DINOv3 para T4 |
| `facebook/dinov3-vith16plus-pretrain-lvd1689m` | 840M | 1280 | ~8 GB | Alta qualidade — cabe na T4 |
| `facebook/dinov3-vit7b16-pretrain-lvd1689m` | 6.7B | 4096 | >15 GB | Nao cabe na T4 — uso em A100/H100 |

---

### DINOv3 ConvNeXt — Meta AI (gated, requer HF_TOKEN)

Arquitetura convolucional (não ViT). Compatível com AutoModel, mas **não usa class token** — o pipeline extrai `pooler_output` automaticamente se disponível, caso contrário aplica global average pooling.

| Model ID | Params | VRAM | Quando usar |
|---|---|---|---|
| `facebook/dinov3-convnext-tiny-pretrain-lvd1689m` | 28M | ~1 GB | CNN leve, alternativa ao ViT-S |
| `facebook/dinov3-convnext-small-pretrain-lvd1689m` | 50M | ~2 GB | CNN intermediária |
| `facebook/dinov3-convnext-base-pretrain-lvd1689m` | 88M | ~3 GB | CNN robusta |
| `facebook/dinov3-convnext-large-pretrain-lvd1689m` | 198M | ~5 GB | Melhor CNN DINOv3 |

> **Atenção:** para usar os ConvNeXt é necessário verificar o formato de saída do modelo e ajustar a extração de embeddings no `embedder.py` se necessário.

---

### BioCLIP — Imageomics (público, MIT)

Modelo CLIP treinado especificamente em 10 milhões de imagens biológicas do Tree of Life (450K+ taxa). **O mais adequado do ponto de vista biológico** para identificação de espécies de abelhas.

| Model ID | Params | Dim | VRAM | Observações |
|---|---|---|---|---|
| `imageomics/bioclip` | 86M | 512 | ~2 GB | Público, MIT — treinado em Tree of Life 10M |

O BioCLIP é suportado nativamente pelo pipeline via `BioCLIPEmbedder`. Para usá-lo, instale a dependência extra antes de executar o pipeline:

```bash
pip install open_clip_torch
# ou, dentro do ambiente do projeto:
pip install "beeai[bioclip]"
```

No Kaggle, adicione uma célula antes da Célula 9:

```python
!pip install open_clip_torch -q
```

Depois basta definir na Célula 2:

```python
ENCODER_NAME = "imageomics/bioclip"
MODEL_VERSION = "bioclip_mlp_v001"
```

---

Para trocar o encoder, altere `ENCODER_NAME` na Célula 2 e atualize `MODEL_VERSION` com um nome que reflita o encoder usado.

---

## Usando suas próprias imagens (ao invés do GBIF)

O pipeline padrão baixa imagens automaticamente do GBIF. Para treinar com imagens próprias:

### Opção A — Substituir o catálogo diretamente

Após clonar o repositório no Kaggle (Célula 4), copie seu `raw_catalog.csv` para:
```
/kaggle/working/identificadordeabelha/data/raw/metadata/raw_catalog.csv
```

O CSV precisa ter as colunas:
```
image_id, specimen_id, species_code, file_path, source, view_type,
annotator, label_status, sha256, scientific_name, gbif_key,
occurrence_url, image_url, license, rights_holder, publisher, dataset_name
```

Em seguida, **pule a Célula 7** (download do GBIF) e execute a partir da Célula 8.

### Opção B — Dataset Kaggle

Adicione seu dataset de imagens como **Kaggle Dataset** e acesse em `/kaggle/input/nome-do-dataset/`. Ajuste os paths nas células conforme necessário.

---

## Execução passo a passo

| Célula | O que faz | Tempo estimado |
|---|---|---|
| 1 | Verifica GPU e CUDA | Segundos |
| 2 | Define configurações | Segundos |
| 3 | Carrega secrets do Kaggle | Segundos |
| 4 | Clona o repositório | ~30s |
| 5 | Instala dependências (`pip install`) | ~3 min |
| 6 | Cria diretórios e `.env` | Segundos |
| 7 | Baixa imagens do GBIF | ~8–25 min (depende de `IMAGES_PER_SPECIES`) |
| 8 | Verifica dataset | Segundos |
| 9 | Pipeline completo de treino | ~5–15 min (GPU) |
| 10 | Exibe métricas e matriz de confusão | Segundos |
| 11 | Zippa artefatos para download | Segundos |

**Tempo total estimado:** 20–45 minutos dependendo do encoder e número de imagens.

---

## Erros comuns e soluções

### `Could not resolve host: github.com`

**Causa:** Internet desativada no notebook.

**Solução:** Painel direito → **Settings → Internet → ativar o toggle**. Re-execute a Célula 4.

---

### GPU aparece como `None` (não consegue selecionar)

**Causa:** Telefone não verificado na conta Kaggle.

**Solução:** [kaggle.com/settings](https://kaggle.com/settings) → **Phone Verification → Verify**. Depois volte ao notebook e selecione GPU T4.

---

### `GITHUB_TOKEN não encontrado — usando sem token`

**Causa:** O secret não foi adicionado ou o nome está errado.

**Solução:** Dentro do notebook → **Add-ons → Secrets** → confirme que o nome é exatamente `GITHUB_TOKEN` (maiúsculas, sem espaços). Se o repositório for público, este erro pode ser ignorado.

---

### `ValueError: Invalid format specifier` na Célula 10

**Causa:** Bug de f-string em versões antigas do notebook (já corrigido).

**Solução:** Pule a Célula 10 e execute a Célula 11 diretamente — o treino já ocorreu com sucesso. Para a próxima vez, re-importe o notebook do repositório (versão corrigida).

---

### `fatal: repository not found` ou `403` ao clonar

**Causa:** Token inválido, expirado ou sem permissão `repo`.

**Solução:** Gere um novo token no GitHub (Settings → Developer settings → Personal access tokens → Tokens classic) com permissão `repo`. Atualize o secret no Kaggle.

---

### Poucas imagens retornadas pelo GBIF

**Causa:** O GBIF tem disponibilidade variável por espécie. Algumas espécies têm menos registros públicos.

**Solução:** O pipeline continua normalmente com menos imagens. Se o dataset ficou muito desbalanceado (ex: uma espécie com menos de 20 imagens), os resultados do modelo serão fracos — considere aumentar o `IMAGES_PER_SPECIES` ou adicionar `--allow-all-licenses` (já incluído por padrão no notebook).

---

## Baixar e usar os artefatos localmente

### 1. Baixar do Kaggle

Após a Célula 11 executar, o arquivo `MODEL_VERSION.zip` fica em `/kaggle/working/`.

Painel direito → **Output → Download output files** → selecione o `.zip`.

### 2. Extrair localmente

```bash
unzip dinov2_small_mlp_v001.zip -d artifacts/models/
```

### 3. Registrar no banco de dados local

```bash
cd backend
python - <<'EOF'
from beeai.core.config import get_settings
from beeai.db.session import get_session_factory, init_db
from beeai.repositories.model_repository import ModelRepository
from pathlib import Path

settings = get_settings()
init_db(settings)
factory = get_session_factory(settings.database_url)
with factory() as db:
    ModelRepository().register_model_version(
        db,
        version="dinov2_small_mlp_v001",       # mesma versão do treino
        encoder_name="facebook/dinov2-small",   # mesmo encoder do treino
        classifier_type="mlp",
        artifact_dir=Path("../artifacts/models/dinov2_small_mlp_v001").resolve(),
        metrics={},
        activate=True,
    )
    db.commit()
    print("Modelo registrado.")
EOF
```

### 4. Organizar modelos antigos

Modelos que não estão mais em uso ficam em `artifacts/Modelos Antigos/` — diretório local, não versionado no git. Para mover um modelo:

```bash
mv artifacts/models/dinov2_small_mlp_v001 "artifacts/Modelos Antigos/"
```

---

## Checklist para um novo ciclo de treino

- [ ] Definir nome único para `MODEL_VERSION` na Célula 2
- [ ] Escolher `ENCODER_NAME` (dinov2-small para iterações rápidas, dinov2-base para produção)
- [ ] Ajustar `IMAGES_PER_SPECIES` conforme disponibilidade de tempo
- [ ] Confirmar que GPU T4 e Internet estão ativos nas Settings
- [ ] Executar todas as células em ordem
- [ ] Baixar o `.zip` da aba Output
- [ ] Extrair em `artifacts/models/` e registrar no banco
