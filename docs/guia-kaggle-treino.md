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
| `MODEL_VERSION` | Sempre — cada treino precisa de um nome único | `dinov2_base_mlp_v001`, `dinov2_small_mlp_v002` |
| `ENCODER_NAME` | Quando quiser testar um encoder diferente | ver tabela abaixo |
| `IMAGES_PER_SPECIES` | Quando quiser mais dados ou treino mais rápido | 50 (demo), 150 (padrão), 300+ (produção) |

> **Convenção de nome:** `{encoder}_{classificador}_{versao}` — ex: `dinov2_base_mlp_v002`

---

## DINOv2 no Kaggle

O projeto usa encoders da família **DINOv2** da Meta AI, disponíveis publicamente no HuggingFace. Todos funcionam no Kaggle sem token.

| Model ID no HuggingFace | Nome interno | VRAM usada | Qualidade |
|---|---|---|---|
| `facebook/dinov2-small` | DINOv2-S | ~1 GB | Boa — uso em demos e validação |
| `facebook/dinov2-base` | DINOv2-B (DINOv3 no projeto) | ~2 GB | Melhor — uso em produção |
| `facebook/dinov2-large` | DINOv2-L | ~5 GB | Excelente — treino mais lento |
| `facebook/dinov2-giant` | DINOv2-G | ~10 GB | Máxima — ~14 GB VRAM, cabe na T4 |

> **Nota sobre "DINOv3":** o projeto internamente chama `facebook/dinov2-base` de "DINOv3" por ser a versão mais robusta em uso. Não há um modelo oficial chamado DINOv3 no HuggingFace — use os IDs da tabela acima.

Para trocar o encoder, basta alterar `ENCODER_NAME` na Célula 2 e atualizar `MODEL_VERSION` com um nome que reflita o encoder usado.

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
