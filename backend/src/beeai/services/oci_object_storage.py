from __future__ import annotations

import os
from pathlib import Path

from beeai.core.config import Settings, get_settings


def _make_client(settings: Settings):
    try:
        import oci
    except ImportError:
        raise RuntimeError(
            "OCI SDK nao instalado. Execute: pip install 'beeai[oci]'"
        )

    if settings.oci_use_instance_principal:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    else:
        config = oci.config.from_file(profile_name=settings.oci_config_profile)
        client = oci.object_storage.ObjectStorageClient(config)

    return client


class OciStorageService:
    """Upload e download de arquivos no OCI Object Storage."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = _make_client(self.settings)

    @property
    def namespace(self) -> str:
        if self.settings.oci_namespace:
            return self.settings.oci_namespace
        # Busca o namespace automaticamente se nao configurado
        return self._client.get_namespace().data

    def upload_file(self, local_path: Path, bucket: str, object_name: str) -> None:
        with local_path.open("rb") as f:
            self._client.put_object(
                namespace_name=self.namespace,
                bucket_name=bucket,
                object_name=object_name,
                put_object_body=f,
            )

    def download_file(self, bucket: str, object_name: str, local_path: Path) -> None:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        response = self._client.get_object(
            namespace_name=self.namespace,
            bucket_name=bucket,
            object_name=object_name,
        )
        local_path.write_bytes(response.data.content)

    def upload_directory(self, local_dir: Path, bucket: str, prefix: str = "") -> list[str]:
        uploaded: list[str] = []
        for file in local_dir.rglob("*"):
            if not file.is_file():
                continue
            rel = file.relative_to(local_dir)
            object_name = f"{prefix}/{rel.as_posix()}" if prefix else rel.as_posix()
            self.upload_file(file, bucket, object_name)
            uploaded.append(object_name)
        return uploaded

    def download_directory(self, bucket: str, prefix: str, local_dir: Path) -> list[Path]:
        downloaded: list[Path] = []
        objects = self.list_objects(bucket, prefix)
        for object_name in objects:
            rel = object_name[len(prefix):].lstrip("/")
            local_path = local_dir / rel
            self.download_file(bucket, object_name, local_path)
            downloaded.append(local_path)
        return downloaded

    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        names: list[str] = []
        page = None
        while True:
            kwargs = dict(
                namespace_name=self.namespace,
                bucket_name=bucket,
                prefix=prefix or None,
            )
            if page:
                kwargs["page"] = page
            resp = self._client.list_objects(**kwargs)
            names.extend(obj.name for obj in resp.data.objects)
            if not resp.data.next_start_with:
                break
            page = resp.data.next_start_with
        return names

    def ensure_bucket(self, bucket: str, compartment_id: str) -> None:
        try:
            import oci
        except ImportError:
            raise RuntimeError("OCI SDK nao instalado.")

        try:
            self._client.get_bucket(self.namespace, bucket)
        except oci.exceptions.ServiceError as e:
            if e.status != 404:
                raise
            self._client.create_bucket(
                namespace_name=self.namespace,
                create_bucket_details=oci.object_storage.models.CreateBucketDetails(
                    name=bucket,
                    compartment_id=compartment_id,
                    storage_tier="Standard",
                    public_access_type="NoPublicAccess",
                ),
            )
