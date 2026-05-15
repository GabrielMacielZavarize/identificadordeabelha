# Guia de Setup — Supabase + Hugging Face + Vercel

Passo a passo para colocar o BeeAI no ar com autenticação, banco de dados em nuvem
e hospedagem separada de backend e frontend.

---

## Visão geral da arquitetura

```
┌─────────────────────┐     HTTPS / JWT     ┌──────────────────────────┐
│  Frontend (Vercel)  │ ──────────────────► │  Backend (HF Spaces)     │
│  React + Vite       │                     │  FastAPI + PyTorch       │
└─────────────────────┘                     └──────────┬───────────────┘
         │                                             │
         │ Supabase JS SDK                             │ SQLAlchemy (psycopg2)
         ▼                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Supabase                                   │
│   Auth (JWT)  ·  PostgreSQL  ·  Storage (opcional)                  │
└─────────────────────────────────────────────────────────────────────┘

Expo (mobile) ──► mesmo backend ──► mesmo Supabase
```

---

## Parte 1 — Supabase

### 1.1 Criar o projeto

1. Acesse [supabase.com](https://supabase.com) e crie uma conta (gratuito).
2. Clique em **New project**.
3. Escolha um nome (ex: `beeai`), senha forte para o banco, e região mais próxima (ex: `South America (São Paulo)`).
4. Aguarde o projeto inicializar (~2 min).

### 1.2 Pegar as credenciais

Vá em **Settings → API** e copie:

| Variável | Onde fica |
|---|---|
| `SUPABASE_URL` | "Project URL" |
| `SUPABASE_ANON_KEY` | "Project API keys → anon public" |
| `SUPABASE_JWT_SECRET` | Settings → API → JWT Settings → **JWT Secret** |

E em **Settings → Database → Connection string → URI** copie a URL do banco PostgreSQL.
Ela terá o formato:
```
postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

### 1.3 Configurar Auth (Supabase Dashboard)

1. **Authentication → Providers → Email**: ative "Confirm email" apenas se quiser e-mail de confirmação obrigatório.
2. **Authentication → URL Configuration**:
   - Site URL: `https://seu-projeto.vercel.app`
   - Redirect URLs: `https://seu-projeto.vercel.app/**`

### 1.4 Migrar o banco

O projeto usa Alembic para migrations. Com o `DATABASE_URL` apontando para o Supabase:

```bash
cd backend

# Copie e preencha o .env
cp .env.example .env
# Edite: BEEAI_DATABASE_URL=postgresql://postgres.<ref>:<senha>@...

# Rode as migrations
.venv/bin/alembic upgrade head

# Popule as espécies (seed)
.venv/bin/python scripts/seed_species.py
```

---

## Parte 2 — Hugging Face Spaces (Backend)

### 2.1 Criar o Space

1. Acesse [huggingface.co](https://huggingface.co) e crie conta (gratuito).
2. Clique em **New Space**.
3. Configurações:
   - **Space name**: `beeai-backend`
   - **SDK**: Docker
   - **Visibility**: Public (ou Private — mas Private exige plano pago para API externa)
   - **Hardware**: CPU Basic (gratuito) ou T4 Small se precisar GPU

### 2.2 Configurar o README.md do Space

O HF Spaces lê um `README.md` com metadados especiais. Crie (ou ajuste) o arquivo
`backend/README.md` com:

```markdown
---
title: BeeAI Backend
emoji: 🐝
colorFrom: blue
colorTo: yellow
sdk: docker
pinned: false
---

Backend FastAPI do BeeAI — identificação de espécies de abelhas.
```

### 2.3 Secrets no HF Spaces

No painel do Space vá em **Settings → Variables and secrets** e adicione:

| Secret | Valor |
|---|---|
| `BEEAI_DATABASE_URL` | URL PostgreSQL do Supabase |
| `BEEAI_SUPABASE_URL` | URL do projeto Supabase |
| `BEEAI_SUPABASE_ANON_KEY` | Anon key do Supabase |
| `BEEAI_SUPABASE_JWT_SECRET` | JWT Secret do Supabase |
| `BEEAI_CORS_ORIGINS` | `["https://seu-projeto.vercel.app"]` |
| `BEEAI_UPLOAD_DIR` | `/data/uploads` |
| `BEEAI_ARTIFACTS_DIR` | `/data/models` |
| `HF_TOKEN` | Seu token HF (se modelo for gated) |

> O HF Spaces injeta os secrets como variáveis de ambiente — o backend lê automaticamente via `pydantic-settings`.

### 2.4 Fazer o deploy

O HF Spaces faz o deploy direto de um repositório git. Você tem duas opções:

**Opção A — Repositório separado para o backend (recomendado):**
```bash
# Clone o Space vazio que o HF cria
git clone https://huggingface.co/spaces/seu-usuario/beeai-backend
cd beeai-backend

# Copie o conteúdo do backend do projeto
cp -r /caminho/para/identificadordeabelha/backend/* .

# Commit e push
git add .
git commit -m "Initial deploy"
git push
```

**Opção B — Apontar para um subdiretório (via Docker):**
Configure o Space para usar o `Dockerfile` em `backend/` via `Dockerfile path` nas configurações avançadas.

### 2.5 Verificar o deploy

Após o build terminar (pode levar 10-15 min na primeira vez por causa do PyTorch),
acesse `https://seu-usuario-beeai-backend.hf.space/api/v1/health`.

---

## Parte 3 — Vercel (Frontend)

### 3.1 Criar o projeto no Vercel

1. Acesse [vercel.com](https://vercel.com) e faça login com GitHub.
2. Clique em **Add New → Project**.
3. Importe o repositório `identificadordeabelha`.
4. Configurações do projeto:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 Variáveis de ambiente no Vercel

Em **Settings → Environment Variables** adicione:

| Variável | Valor |
|---|---|
| `VITE_SUPABASE_URL` | URL do projeto Supabase |
| `VITE_SUPABASE_ANON_KEY` | Anon key do Supabase |
| `VITE_API_BASE_URL` | `https://seu-usuario-beeai-backend.hf.space/api/v1` |

### 3.3 Deploy

Cada push para `main` dispara um deploy automático no Vercel.
Para forçar manualmente: **Deployments → Redeploy**.

---

## Parte 4 — Expo / React Native (Mobile)

O app mobile usa o **mesmo backend** e o **mesmo Supabase**.

### 4.1 Instalar dependências no projeto Expo

```bash
cd seu-app-expo
npx expo install @supabase/supabase-js @react-native-async-storage/async-storage
```

### 4.2 Configurar o cliente Supabase no Expo

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
import AsyncStorage from '@react-native-async-storage/async-storage'

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      storage: AsyncStorage,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  }
)
```

### 4.3 Variáveis de ambiente no Expo

Crie `seu-app-expo/.env`:
```
EXPO_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJ...
EXPO_PUBLIC_API_URL=https://seu-usuario-beeai-backend.hf.space/api/v1
```

### 4.4 Enviar o token JWT para o backend

```typescript
// lib/api.ts
import axios from 'axios'
import { supabase } from './supabase'

export const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,
})

api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
```

---

## Parte 5 — Variáveis de ambiente resumidas

### backend/.env (local) ou Secrets no HF Spaces

```env
BEEAI_PROJECT_NAME=BeeAI
BEEAI_DEBUG=false
BEEAI_DATABASE_URL=postgresql://postgres.<ref>:<senha>@...
BEEAI_UPLOAD_DIR=/data/uploads
BEEAI_ARTIFACTS_DIR=/data/models
BEEAI_MAX_UPLOAD_SIZE_MB=15
BEEAI_CORS_ORIGINS=["http://localhost:5173","https://seu-projeto.vercel.app"]
BEEAI_SUPABASE_URL=https://<project-ref>.supabase.co
BEEAI_SUPABASE_ANON_KEY=eyJ...
BEEAI_SUPABASE_JWT_SECRET=seu-jwt-secret
HF_TOKEN=hf_...
```

### frontend/.env.local (local) ou Env Vars no Vercel

```env
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_API_BASE_URL=https://seu-usuario-beeai-backend.hf.space/api/v1
```

---

## Checklist de go-live

- [ ] Projeto Supabase criado e banco migrado (`alembic upgrade head`)
- [ ] Seed de espécies executado (`python scripts/seed_species.py`)
- [ ] Space HF criado com Dockerfile, README.md com metadados e secrets configurados
- [ ] Backend acessível em `https://...hf.space/api/v1/health`
- [ ] Projeto Vercel criado com root em `frontend/` e variáveis de ambiente
- [ ] `BEEAI_CORS_ORIGINS` inclui a URL do Vercel
- [ ] `Authentication → URL Configuration` no Supabase com a URL do Vercel
- [ ] Login e cadastro funcionando no frontend
- [ ] Upload de imagem e classificação funcionando autenticado
- [ ] App Expo conectando no mesmo backend (testar com Expo Go)
