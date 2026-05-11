#!/usr/bin/env bash
# Configura o ambiente de treinamento em uma VM GPU OCI (Ubuntu 22.04).
# Rodar com: bash setup_oci_vm.sh
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/GabrielMacielZavarize/identificadordeabelha.git}"
REPO_DIR="$HOME/identificadordeabelha"

echo "=== [1/5] Atualizando sistema e instalando dependencias base ==="
sudo apt-get update -q
sudo apt-get install -y -q git python3.12 python3.12-venv python3-pip curl

echo "=== [2/5] Clonando repositorio ==="
if [ ! -d "$REPO_DIR" ]; then
    git clone "$REPO_URL" "$REPO_DIR"
else
    echo "Repositorio ja existe, atualizando..."
    git -C "$REPO_DIR" pull
fi

cd "$REPO_DIR/backend"

echo "=== [3/5] Criando ambiente virtual e instalando pacotes ==="
python3.12 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip -q
pip install -e ".[oci]" -q

echo "=== [4/5] Verificando GPU ==="
python - <<'EOF'
import torch
if torch.cuda.is_available():
    print(f"  GPU detectada: {torch.cuda.get_device_name(0)}")
    print(f"  Memoria: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("  AVISO: CUDA nao disponivel. Verifique os drivers NVIDIA.")
EOF

echo "=== [5/5] Pronto! ==="
echo ""
echo "Proximos passos:"
echo "  1. Configure o .env em backend/.env com as variaveis OCI"
echo "  2. Baixe o dataset: python scripts/oci_sync.py download-dataset --local-dir data/raw/gbif"
echo "  3. Execute o pipeline: python scripts/run_training_pipeline.py --raw-catalog ..."
echo "  4. Envie os artefatos: python scripts/oci_sync.py upload-artifacts --version <versao>"
