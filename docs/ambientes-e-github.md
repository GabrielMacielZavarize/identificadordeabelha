# Ambientes e Fluxo de Desenvolvimento

## Visão geral

O projeto usa **três ambientes** mapeados em branches dedicadas no GitHub. Cada ambiente tem configurações próprias de Docker, variáveis de ambiente e regras de acesso.

```
develop ──► staging ──► main
  (dev)    (homolog)   (prod)
```

---

## Ambientes

### Dev (`develop`)

Ambiente de trabalho diário. Hot reload ativo, código-fonte montado como volume (mudanças refletem imediato no container, sem rebuild).

| Item | Valor |
|------|-------|
| Frontend | `http://localhost:5173` |
| Backend | `http://localhost:8001` |
| Debug | ativado |
| Hot reload | sim |
| Imagens servidas por | proxy Vite → backend |

**Como subir:**
```bash
docker compose up
# ou, se quiser rebuild:
docker compose up --build
```

> `docker compose up` sem flags já carrega o `docker-compose.override.yml` automaticamente — esse é o comportamento padrão do Docker Compose.

---

### Staging (`staging`)

Ambiente de homologação. Simula produção: frontend é compilado (`npm run build`), sem hot reload, sem volume de código-fonte. Usado para validar funcionalidades antes de ir para prod.

| Item | Valor |
|------|-------|
| Frontend | `http://localhost:4173` |
| Backend | `http://localhost:8002` |
| Debug | ativado (para facilitar análise de erros) |
| Hot reload | não |
| Imagens servidas por | backend direto (`http://localhost:8002/uploads/...`) |

**Como subir:**
```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml up --build
```

> O primeiro `up` em staging demora mais porque roda `npm run build` dentro do container.

---

### Prod (`main`)

Ambiente de produção. Frontend compilado, backend com 2 workers, debug desativado.

| Item | Valor |
|------|-------|
| Frontend | `http://localhost` (porta 80) |
| Backend | `http://localhost:8000` |
| Debug | desativado |
| Hot reload | não |
| Workers | 2 |

**Como subir:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

> Porta 80 requer permissão de root ou configuração de `authbind` em alguns sistemas Linux. Se der erro de permissão, mude `"80:4173"` para `"3000:4173"` no `docker-compose.prod.yml`.

---

## Aplicar migrações de banco

Sempre que uma nova migration for criada, rode o comando abaixo no ambiente correspondente:

**Dev:**
```bash
docker compose exec backend bash -c "cd /app/backend && PYTHONPATH=/app/backend/.venv/lib/python3.12/site-packages /usr/local/bin/python3 -c 'from alembic.config import main; main()' upgrade head"
```

**Staging:**
```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend bash -c "cd /app/backend && PYTHONPATH=/app/backend/.venv/lib/python3.12/site-packages /usr/local/bin/python3 -c 'from alembic.config import main; main()' upgrade head"
```

**Prod:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend bash -c "cd /app/backend && PYTHONPATH=/app/backend/.venv/lib/python3.12/site-packages /usr/local/bin/python3 -c 'from alembic.config import main; main()' upgrade head"
```

> Se o banco foi criado fora do Alembic (via `init_db.py`), rode o `stamp` antes do `upgrade`:
> ```bash
> # substitua VERSION pela última migration existente antes da nova
> ... python3 -c '...' stamp VERSION
> ... python3 -c '...' upgrade head
> ```

---

## Estrutura de arquivos Docker

```
docker-compose.yml           ← base (build, volumes compartilhados)
docker-compose.override.yml  ← dev (carregado automaticamente)
docker-compose.staging.yml   ← staging (precisa especificar com -f)
docker-compose.prod.yml      ← prod (precisa especificar com -f)
```

---

## Fluxo de branches no GitHub

### Branches

| Branch | Ambiente | Quem faz push direto |
|--------|----------|----------------------|
| `develop` | Dev | Qualquer membro do time |
| `staging` | Homolog | Ninguém — só via PR |
| `main` | Prod | Ninguém — só via PR revisado |

### Fluxo de trabalho

```
1. Crie uma branch de feature a partir de develop:
   git checkout develop
   git pull origin develop
   git checkout -b feature/nome-da-funcionalidade

2. Desenvolva e faça commits na feature branch.

3. Abra PR: feature/xxx → develop
   - CI roda testes automaticamente
   - Merge direto (sem review obrigatório)

4. Quando develop estiver estável, abra PR: develop → staging
   - CI roda testes
   - Pelo menos 1 review obrigatório
   - Merge só após CI passar

5. Após validação em staging, abra PR: staging → main
   - CI roda testes
   - Pelo menos 1 review obrigatório
   - Merge só após CI passar e review aprovado
```

### Configurar proteção de branches no GitHub

Acesse: **GitHub → Settings → Branches → Add branch ruleset**

**Regra para `main`:**
- Branch name pattern: `main`
- Require a pull request before merging: **ativado**
- Required approvals: **1**
- Require status checks to pass: **ativado**
  - `Backend tests`
  - `Frontend tests`
- Block force pushes: **ativado**
- Restrict deletions: **ativado**

**Regra para `staging`:**
- Branch name pattern: `staging`
- Require a pull request before merging: **ativado**
- Required approvals: **1**
- Require status checks to pass: **ativado**
  - `Backend tests`
  - `Frontend tests`
- Block force pushes: **ativado**

**`develop` não tem proteção** — push direto liberado para agilidade no dia a dia.

O workflow em `.github/workflows/ci.yml` roda automaticamente em `push` e `pull_request` para `develop`, `staging` e `main`.

---

## Configurar branches no repositório local

```bash
# Criar e enviar as branches a partir da branch atual do repositório.
# Neste projeto, a branch inicial no GitHub era master.
git checkout master
git pull origin master

git checkout -b main
git push -u origin main

git checkout -b staging
git push -u origin staging

git checkout -b develop
git push -u origin develop

# Definir develop como branch padrão do repositório
# GitHub → Settings → General → Default branch → develop
```

Depois que `develop` estiver como branch padrão e as proteções estiverem ativas, `master` pode ser removida se não houver mais dependência dela.

---

## Referência rápida de comandos

| Ação | Comando |
|------|---------|
| Subir dev | `docker compose up` |
| Subir staging | `docker compose -f docker-compose.yml -f docker-compose.staging.yml up --build` |
| Subir prod | `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build` |
| Parar qualquer ambiente | `docker compose down` |
| Ver logs | `docker compose logs -f` |
| Rebuild sem cache | `docker compose build --no-cache` |
