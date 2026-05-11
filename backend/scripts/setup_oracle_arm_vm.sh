#!/usr/bin/env bash
# BeeAI — Setup completo para Oracle Always Free VM (VM.Standard.A1.Flex / Ubuntu 22.04 ARM64)
# Uso: bash setup_oracle_arm_vm.sh https://github.com/SEU_USUARIO/identificadordeabelha
#
# O que este script faz:
#   1. Atualiza o sistema e instala dependências
#   2. Instala Python 3.12, Node.js 20, nginx
#   3. Clona o repositório
#   4. Instala o pacote Python (beeai) no virtualenv
#   5. Constrói o frontend
#   6. Cria o .env com os caminhos corretos e o IP público da VM
#   7. Inicializa o banco de dados (alembic upgrade head)
#   8. Configura nginx (frontend estático + proxy da API)
#   9. Configura serviço systemd para o backend
#  10. Abre as portas 80 e 8000 no firewall do SO

set -euo pipefail

# ── Variáveis ────────────────────────────────────────────────────────────────

REPO_URL="${1:-}"
REPO_DIR="/opt/beeai"
BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/frontend"
DATA_DIR="$REPO_DIR/data"
ARTIFACTS_DIR="$REPO_DIR/artifacts/models"
VENV="$BACKEND_DIR/.venv"
SERVICE_USER="ubuntu"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[beeai]${NC} $*"; }
warn() { echo -e "${YELLOW}[aviso]${NC} $*"; }
die()  { echo -e "${RED}[erro]${NC} $*"; exit 1; }

# ── Validações iniciais ───────────────────────────────────────────────────────

[[ $EUID -ne 0 ]] && die "Execute com sudo: sudo bash $0 $*"
[[ -z "$REPO_URL" ]] && die "Informe a URL do repositório: sudo bash $0 https://github.com/USUARIO/identificadordeabelha"

# ── Detectar IP público da VM ─────────────────────────────────────────────────

log "Detectando IP público..."
VM_IP=$(curl -sf --max-time 5 http://ifconfig.me || hostname -I | awk '{print $1}')
log "IP público: $VM_IP"

# ── 1. Atualizar sistema ──────────────────────────────────────────────────────

log "Atualizando sistema..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

# ── 2. Instalar dependências de sistema ───────────────────────────────────────

log "Instalando dependências de sistema..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  git curl wget ca-certificates gnupg \
  build-essential libgomp1 \
  software-properties-common \
  nginx \
  iptables-persistent netfilter-persistent

# Python 3.12 via deadsnakes PPA (Ubuntu 22.04 vem com 3.10)
add-apt-repository ppa:deadsnakes/ppa -y >/dev/null 2>&1
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  python3.12 python3.12-venv python3.12-dev python3.12-distutils

# Node.js 20 para build do frontend
if ! command -v node &>/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1
  apt-get install -y -qq nodejs
fi

log "Python: $(python3.12 --version)"
log "Node:   $(node --version)"

# ── 3. Clonar repositório ─────────────────────────────────────────────────────

if [[ -d "$REPO_DIR/.git" ]]; then
  log "Repositório já existe — atualizando..."
  git -C "$REPO_DIR" pull --ff-only
else
  log "Clonando repositório..."
  git clone "$REPO_URL" "$REPO_DIR"
  chown -R "$SERVICE_USER:$SERVICE_USER" "$REPO_DIR"
fi

# ── 4. Criar diretórios de dados ──────────────────────────────────────────────

log "Criando diretórios..."
for d in \
  "$DATA_DIR/db" \
  "$DATA_DIR/uploads" \
  "$DATA_DIR/raw" \
  "$DATA_DIR/interim" \
  "$DATA_DIR/processed" \
  "$ARTIFACTS_DIR"
do
  mkdir -p "$d"
done
chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR" "$REPO_DIR/artifacts"

# ── 5. Instalar pacote Python no virtualenv ───────────────────────────────────

log "Criando virtualenv Python 3.12..."
sudo -u "$SERVICE_USER" python3.12 -m venv "$VENV"

log "Instalando beeai e dependências (pode levar alguns minutos)..."
sudo -u "$SERVICE_USER" "$VENV/bin/pip" install --upgrade pip -q
sudo -u "$SERVICE_USER" "$VENV/bin/pip" install -e "$BACKEND_DIR" -q

# ── 6. Configurar .env ────────────────────────────────────────────────────────

log "Configurando .env..."
ENV_FILE="$REPO_DIR/.env"
cat > "$ENV_FILE" <<EOF
BEEAI_DEBUG=false
BEEAI_DATABASE_URL=sqlite:///$DATA_DIR/db/app.sqlite3
BEEAI_UPLOAD_DIR=$DATA_DIR/uploads
BEEAI_ARTIFACTS_DIR=$ARTIFACTS_DIR
BEEAI_CORS_ORIGINS=["http://$VM_IP"]
BEEAI_UPLOADS_BASE_URL=http://$VM_IP
BEEAI_MAX_UPLOAD_SIZE_MB=15
EOF
chown "$SERVICE_USER:$SERVICE_USER" "$ENV_FILE"
log ".env criado em $ENV_FILE"
warn "Se tiver HF_TOKEN, adicione manualmente: echo 'HF_TOKEN=seu_token' >> $ENV_FILE"

# ── 7. Inicializar banco de dados ─────────────────────────────────────────────

log "Inicializando banco de dados (alembic upgrade head)..."
cd "$BACKEND_DIR"
sudo -u "$SERVICE_USER" "$VENV/bin/python" -m alembic upgrade head

# ── 8. Construir frontend ─────────────────────────────────────────────────────

log "Instalando dependências do frontend..."
cd "$FRONTEND_DIR"
sudo -u "$SERVICE_USER" npm ci --silent

log "Construindo frontend (VITE_API_BASE_URL=http://$VM_IP/api/v1)..."
sudo -u "$SERVICE_USER" \
  VITE_API_BASE_URL="http://$VM_IP/api/v1" \
  npm run build

log "Build do frontend concluído em $FRONTEND_DIR/dist"

# ── 9. Configurar nginx ───────────────────────────────────────────────────────

log "Configurando nginx..."
cat > /etc/nginx/sites-available/beeai <<NGINX
server {
    listen 80;
    server_name $VM_IP _;

    # Arquivos estáticos do frontend
    root $FRONTEND_DIR/dist;
    index index.html;

    # Imagens enviadas via upload
    location /uploads/ {
        alias $DATA_DIR/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy para o backend FastAPI
    location /api/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
        client_max_body_size 20M;
    }

    # SPA: qualquer rota desconhecida serve o index.html
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/beeai /etc/nginx/sites-enabled/beeai
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx
log "nginx configurado."

# ── 10. Configurar serviço systemd para o backend ─────────────────────────────

log "Configurando serviço systemd beeai-backend..."
cat > /etc/systemd/system/beeai-backend.service <<SYSTEMD
[Unit]
Description=BeeAI Backend (FastAPI/uvicorn)
After=network.target

[Service]
Type=exec
User=$SERVICE_USER
WorkingDirectory=$BACKEND_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV/bin/uvicorn beeai.api.main:app \\
    --host 127.0.0.1 \\
    --port 8000 \\
    --workers 2 \\
    --app-dir src
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable beeai-backend
systemctl restart beeai-backend
log "Serviço beeai-backend iniciado."

# ── 11. Abrir portas no firewall do SO ────────────────────────────────────────

log "Abrindo portas 80 e 8000 no iptables..."
iptables -I INPUT -p tcp --dport 80  -j ACCEPT 2>/dev/null || true
iptables -I INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
iptables -I INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null || true
netfilter-persistent save >/dev/null 2>&1 || true

# ── Resumo final ──────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             BeeAI instalado com sucesso!                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Frontend:  http://$VM_IP"
echo "  API docs:  http://$VM_IP/api/v1/docs"
echo ""
echo "  Status do backend:"
echo "    sudo systemctl status beeai-backend"
echo ""
echo "  Logs em tempo real:"
echo "    sudo journalctl -u beeai-backend -f"
echo ""
echo -e "${YELLOW}IMPORTANTE: Abra a porta 80 na Security List da OCI.${NC}"
echo "  OCI Console > Networking > Virtual Cloud Networks >"
echo "  beeai-vcn > Security Lists > Default Security List >"
echo "  Add Ingress Rule > Source: 0.0.0.0/0 > Port: 80"
echo ""
echo -e "${YELLOW}Para adicionar modelos treinados:${NC}"
echo "  scp -r ./artifacts/models/VERSAO ubuntu@$VM_IP:$ARTIFACTS_DIR/"
echo ""
