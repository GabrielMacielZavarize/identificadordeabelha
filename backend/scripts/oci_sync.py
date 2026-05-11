"""
CLI para sincronizar datasets e artefatos com OCI Object Storage.

Uso:
  python scripts/oci_sync.py upload-dataset  --local-dir data/raw/gbif
  python scripts/oci_sync.py download-dataset --local-dir data/raw/gbif
  python scripts/oci_sync.py upload-artifacts --version dinov3_vits16_mlp_v001
  python scripts/oci_sync.py download-artifacts --version dinov3_vits16_mlp_v001
"""

from __future__ import annotations

import argparse
from pathlib import Path

from beeai.core.config import get_settings
from beeai.services.oci_object_storage import OciStorageService


def cmd_upload_dataset(args: argparse.Namespace) -> None:
    settings = get_settings()
    svc = OciStorageService(settings)
    local_dir = Path(args.local_dir).resolve()

    print(f"Enviando {local_dir} -> bucket '{settings.oci_bucket_datasets}' (prefixo: raw/)")
    uploaded = svc.upload_directory(local_dir, settings.oci_bucket_datasets, prefix="raw")
    print(f"  {len(uploaded)} arquivo(s) enviado(s).")


def cmd_download_dataset(args: argparse.Namespace) -> None:
    settings = get_settings()
    svc = OciStorageService(settings)
    local_dir = Path(args.local_dir).resolve()

    print(f"Baixando bucket '{settings.oci_bucket_datasets}' (prefixo: raw/) -> {local_dir}")
    downloaded = svc.download_directory(settings.oci_bucket_datasets, "raw", local_dir)
    print(f"  {len(downloaded)} arquivo(s) baixado(s).")


def cmd_upload_artifacts(args: argparse.Namespace) -> None:
    settings = get_settings()
    svc = OciStorageService(settings)
    version: str = args.version
    local_dir = (settings.artifacts_dir / version).resolve()

    if not local_dir.exists():
        raise SystemExit(f"Diretorio de artefatos nao encontrado: {local_dir}")

    print(f"Enviando {local_dir} -> bucket '{settings.oci_bucket_artifacts}' (prefixo: {version}/)")
    uploaded = svc.upload_directory(local_dir, settings.oci_bucket_artifacts, prefix=version)
    print(f"  {len(uploaded)} arquivo(s) enviado(s).")


def cmd_download_artifacts(args: argparse.Namespace) -> None:
    settings = get_settings()
    svc = OciStorageService(settings)
    version: str = args.version
    local_dir = (settings.artifacts_dir / version).resolve()

    print(f"Baixando bucket '{settings.oci_bucket_artifacts}' (prefixo: {version}/) -> {local_dir}")
    downloaded = svc.download_directory(settings.oci_bucket_artifacts, version, local_dir)
    print(f"  {len(downloaded)} arquivo(s) baixado(s).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sincroniza dados/artefatos com OCI Object Storage.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_up_ds = sub.add_parser("upload-dataset", help="Envia dataset local para OCI.")
    p_up_ds.add_argument("--local-dir", required=True, help="Pasta local do dataset.")

    p_dl_ds = sub.add_parser("download-dataset", help="Baixa dataset do OCI para local.")
    p_dl_ds.add_argument("--local-dir", required=True, help="Pasta local de destino.")

    p_up_art = sub.add_parser("upload-artifacts", help="Envia artefatos de uma versao de modelo.")
    p_up_art.add_argument("--version", required=True, help="Versao do modelo (ex: dinov3_v001).")

    p_dl_art = sub.add_parser("download-artifacts", help="Baixa artefatos de uma versao do OCI.")
    p_dl_art.add_argument("--version", required=True, help="Versao do modelo (ex: dinov3_v001).")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    dispatch = {
        "upload-dataset": cmd_upload_dataset,
        "download-dataset": cmd_download_dataset,
        "upload-artifacts": cmd_upload_artifacts,
        "download-artifacts": cmd_download_artifacts,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
