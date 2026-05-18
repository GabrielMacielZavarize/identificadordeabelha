#!/bin/sh
set -e

ARTIFACTS_DIR="/app/backend/artifacts/models"
mkdir -p "$ARTIFACTS_DIR"

python3 - <<'PYEOF'
import os, shutil
from huggingface_hub import snapshot_download

dest = "/app/backend/artifacts/hf_download"
snapshot_download(
    repo_id="macciell01/beeai-model",
    repo_type="model",
    local_dir=dest,
    allow_patterns="artifacts/models/*",
    token=os.getenv("HF_TOKEN"),
)

src = os.path.join(dest, "artifacts", "models")
dst = "/app/backend/artifacts/models"
for name in os.listdir(src):
    s = os.path.join(src, name)
    d = os.path.join(dst, name)
    if os.path.isdir(s) and not os.path.exists(d):
        shutil.copytree(s, d)

print("Artefatos prontos.")
PYEOF

exec uvicorn beeai.api.main:app --host 0.0.0.0 --port "${PORT:-7860}" --app-dir src
