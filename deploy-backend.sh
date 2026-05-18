#!/bin/bash
set -e

HF_TOKEN="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"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Preparando deploy do backend para HF Spaces..."

rm -rf /tmp/beeai-hf-deploy
mkdir /tmp/beeai-hf-deploy

rsync -a \
  --exclude='.venv' \
  --exclude='.env' \
  --exclude='artifacts' \
  --exclude='__pycache__' \
  --exclude='*.egg-info' \
  --exclude='.pytest_cache' \
  "$REPO_ROOT/backend/." /tmp/beeai-hf-deploy/

cat > /tmp/beeai-hf-deploy/.gitignore << 'EOF'
__pycache__/
*.py[cod]
.venv/
.env
*.egg-info/
.pytest_cache/
EOF

cat > /tmp/beeai-hf-deploy/README.md << 'EOF'
---
title: BeeAI Backend
emoji: 🐝
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
---

# BeeAI Backend

API FastAPI para identificação de espécies de abelhas.
EOF

cd /tmp/beeai-hf-deploy
git init -b main
git config user.email "gabriel.zavarize@engeplus.com.br"
git config user.name "GabrielMacielZavarize"
git add -A
git commit -m "Deploy backend $(date '+%Y-%m-%d %H:%M')"
git remote add huggingface "https://macciell01:${HF_TOKEN}@huggingface.co/spaces/macciell01/beeai-backend"
git push huggingface main --force

echo ""
echo "Backend publicado em: https://macciell01-beeai-backend.hf.space"
