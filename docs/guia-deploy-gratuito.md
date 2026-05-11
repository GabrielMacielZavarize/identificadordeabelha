# BeeAI — Deploy 100% Gratuito: Kaggle + Oracle Always Free

Este guia cobre o fluxo completo:

- **Treino:** Kaggle Notebooks (GPU T4, 30h/semana, sem cartão)
- **Hospedagem:** Oracle Always Free VM ARM (4 OCPUs, 24 GB RAM, para sempre)
- **Storage:** Oracle Object Storage (20 GB, para sempre)

> **Resumo de custos:** R$ 0,00. Sempre.

---

## Visão geral do fluxo

```
[Kaggle]                    [Oracle VM ARM]
  GPU T4 grátis     →         Backend FastAPI
  Treina modelo     →         Frontend React
  Baixa artefatos   →  scp    Serve na internet
```

---

## Parte 1 — Treino no Kaggle

### Passo 1 — Criar conta no Kaggle (2 min)

Acesse [kaggle.com](https://kaggle.com) e crie uma conta. Não precisa de cartão de crédito.

Após criar a conta, vá em **Settings → Phone Verification** e verifique seu número de telefone. Isso libera 30 horas de GPU por semana.

---

### Passo 2 — Adicionar secrets do GitHub (1 min)

Se o seu repositório for privado, você precisa adicionar um token do GitHub para que o Kaggle consiga cloná-lo.

1. Gere um token em: **github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)**
   - Permissão necessária: `repo` → `read`
   - Validade: 90 dias (suficiente para vários ciclos de treino)
2. No Kaggle: **Perfil → Settings → API Secrets → Add new secret**
   - Nome: `GITHUB_TOKEN`
   - Valor: o token gerado

---

### Passo 3 — Criar o notebook no Kaggle

1. Em [kaggle.com/code](https://kaggle.com/code), clique em **New Notebook**
2. No canto superior direito, clique em **File → Import Notebook**
3. Selecione o arquivo `notebooks/04_kaggle_training.ipynb` do seu repositório local
4. Após importar, vá em **Settings (painel direito) → Accelerator → GPU T4**
5. Clique em **Save** para confirmar

---

### Passo 4 — Configurar e executar

Abra a **Célula 2** do notebook e ajuste:

```python
GITHUB_REPO_URL   = "https://github.com/GabrielMacielZavarize/identificadordeabelha"
MODEL_VERSION     = "dinov2_small_mlp_v001"
ENCODER_NAME      = "facebook/dinov2-small"
IMAGES_PER_SPECIES = 150
```

Depois clique em **Run All** (ou `Shift+Enter` célula a célula).

| Etapa | Tempo estimado |
| --- | --- |
| Download das imagens GBIF | ~12 min (150 imgs × 3 espécies) |
| Extração de embeddings (GPU) | ~5 min |
| Treino do MLP | ~2 min |
| Avaliação e empacotamento | ~1 min |
| **Total** | **~20 min** |

---

### Passo 5 — Baixar os artefatos

Após a Célula 11 executar, o arquivo `dinov2_small_mlp_v001.zip` estará disponível.

No painel direito do Kaggle: **Output → Download output files** → selecione o `.zip`.

Extraia localmente:

```bash
unzip dinov2_small_mlp_v001.zip -d artifacts/models/
```

---

## Parte 2 — Deploy na Oracle Always Free

### Passo 1 — Criar a VCN (rede virtual)

**OCI Console → Networking → Virtual Cloud Networks → Start VCN Wizard**

- Escolha: **Create VCN with Internet Connectivity**
- Nome: `beeai-vcn`
- Clique em **Next → Create**

Isso cria automaticamente subnet pública, Internet Gateway e tabela de rotas.

---

### Passo 2 — Criar a VM ARM

**OCI Console → Compute → Instances → Create Instance**

| Campo | Valor |
| --- | --- |
| Name | `beeai-server` |
| Image | Ubuntu 22.04 |
| Shape | **VM.Standard.A1.Flex** |
| OCPUs | 4 |
| RAM | 24 GB |
| VCN | beeai-vcn |
| Subnet | Public subnet |
| SSH key | Upload `~/.ssh/id_rsa.pub` |
| Boot volume | Mínimo 50 GB (padrão 47 GB) |

> **VM.Standard.A1.Flex com 4 OCPUs e 24 GB RAM é Always Free** — use esses valores exatos para não ser cobrado.

Anote o **IP público** da instância após a criação.

---

### Passo 3 — Abrir a porta 80 na Security List da OCI

Por padrão, só a porta 22 (SSH) está aberta.

**OCI Console → Networking → Virtual Cloud Networks → beeai-vcn → Security Lists → Default Security List → Add Ingress Rules**

| Campo | Valor |
| --- | --- |
| Source CIDR | `0.0.0.0/0` |
| IP Protocol | TCP |
| Destination Port Range | `80` |

Clique em **Add Ingress Rules**.

---

### Passo 4 — Executar o script de setup

Do seu computador local, envie o script para a VM:

```bash
scp backend/scripts/setup_oracle_arm_vm.sh ubuntu@IP_DA_VM:~
```

Conecte na VM:

```bash
ssh ubuntu@IP_DA_VM
```

Execute o script (substitua pela URL do seu repositório):

```bash
sudo bash setup_oracle_arm_vm.sh https://github.com/GabrielMacielZavarize/identificadordeabelha
```

O script leva cerca de **10-15 minutos** e configura tudo automaticamente:

| O que faz | Resultado |
| --- | --- |
| Instala Python 3.12, nginx, Node.js | Sistema pronto |
| Clona o repositório | `/opt/beeai/` |
| Instala dependências Python | Virtualenv em `/opt/beeai/backend/.venv` |
| Constrói o frontend | Arquivos estáticos em `/opt/beeai/frontend/dist` |
| Configura nginx | Serve frontend na porta 80, proxy da API |
| Cria serviço systemd | Backend inicia automaticamente no boot |
| Abre portas no iptables | Tráfego HTTP liberado |

---

### Passo 5 — Enviar os artefatos do modelo

De volta no seu computador local, envie o modelo treinado para a VM:

```bash
scp -r artifacts/models/dinov2_small_mlp_v001 ubuntu@IP_DA_VM:/opt/beeai/artifacts/models/
```

Na VM, registre o modelo no banco de dados:

```bash
ssh ubuntu@IP_DA_VM
cd /opt/beeai/backend
source .venv/bin/activate

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
        version="dinov2_small_mlp_v001",
        encoder_name="facebook/dinov2-small",
        classifier_type="mlp",
        artifact_dir=Path("/opt/beeai/artifacts/models/dinov2_small_mlp_v001"),
        metrics={},
        activate=True,
    )
    db.commit()
    print("Modelo registrado com sucesso.")
EOF
```

---

### Passo 6 — Verificar o deploy

Acesse no navegador: `http://IP_DA_VM`

Para verificar o status do backend:

```bash
sudo systemctl status beeai-backend
```

Para ver os logs em tempo real:

```bash
sudo journalctl -u beeai-backend -f
```

A API fica disponível em: `http://IP_DA_VM/api/v1/docs`

---

## Comandos úteis na VM

```bash
# Reiniciar o backend
sudo systemctl restart beeai-backend

# Atualizar o código (após um git push)
cd /opt/beeai && git pull
sudo systemctl restart beeai-backend

# Rebuild do frontend após mudanças
cd /opt/beeai/frontend
VM_IP=$(curl -sf http://ifconfig.me)
VITE_API_BASE_URL="http://$VM_IP/api/v1" npm run build
sudo systemctl reload nginx

# Ver uso de memória
free -h

# Ver uso de CPU e processos
htop
```

---

## Tabela de recursos Oracle Always Free

| Recurso | Limite | Uso no BeeAI |
| --- | --- | --- |
| VM.Standard.A1.Flex | 4 OCPUs + 24 GB RAM | Backend + Frontend |
| Object Storage | 20 GB | Modelos e datasets |
| Outbound bandwidth | 10 TB/mês | Muito acima do necessário |
| Load Balancer | 1 instância | Opcional (nginx já resolve) |

> Esses recursos são **gratuitos para sempre**, não expiram como o Free Trial de 30 dias.

---

## Resumo por ordem de execução

| Quando | O que fazer |
| --- | --- |
| Agora | Criar conta Kaggle + verificar telefone |
| Agora | Importar notebook 04_kaggle_training.ipynb |
| Agora | Configurar secret GITHUB_TOKEN no Kaggle |
| Agora | Executar o pipeline de treino (Run All) |
| Após treino | Baixar o .zip de artefatos |
| Após treino | Criar VCN e VM na Oracle |
| Após criar VM | Abrir porta 80 na Security List |
| Após criar VM | Executar setup_oracle_arm_vm.sh |
| Após setup | Enviar artefatos via scp |
| Após setup | Registrar modelo no banco |
| Pronto | Acessar http://IP_DA_VM |
