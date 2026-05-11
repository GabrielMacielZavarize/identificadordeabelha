from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError

GBIF_OCCURRENCE_SEARCH_URL = "https://api.gbif.org/v1/occurrence/search"
USER_AGENT = "beeai-demo/0.1"
DEFAULT_SPECIES = (
    "Augochloropsis metallica",
    "Augochloropsis callichroa",
    "Augochloropsis ignita",
)
DEFAULT_LICENSE_TOKENS = ("cc0", "by/4.0", "by-nc/4.0")
RAW_CATALOG_COLUMNS = [
    "image_id",
    "specimen_id",
    "species_code",
    "file_path",
    "source",
    "view_type",
    "annotator",
    "label_status",
    "sha256",
    "scientific_name",
    "gbif_key",
    "occurrence_url",
    "image_url",
    "license",
    "rights_holder",
    "publisher",
    "dataset_name",
]


def fetch_json(url: str, params: dict[str, object], *, timeout: int = 30) -> dict[str, Any]:
    request_url = f"{url}?{urlencode(params)}"
    request = Request(request_url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def species_code(scientific_name: str) -> str:
    parts = re.sub(r"[^A-Za-z0-9 ]+", " ", scientific_name).lower().split()
    if len(parts) < 2:
        return re.sub(r"[^a-z0-9]+", "_", scientific_name.lower()).strip("_")
    return f"{parts[0][:3]}_{parts[1]}"


def license_is_allowed(license_value: str, allowed_tokens: tuple[str, ...]) -> bool:
    normalized = license_value.lower()
    return any(token in normalized for token in allowed_tokens)


def image_suffix(image_url: str, content_type: str | None) -> str:
    if content_type and "png" in content_type.lower():
        return ".png"

    suffix = Path(urlparse(image_url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return ".jpg"


def valid_image(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        return False
    return True


def download_image(
    image_url: str,
    output_path: Path,
    *,
    timeout: int = 45,
) -> tuple[Path, str] | None:
    request = Request(image_url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type")
            suffix = image_suffix(image_url, content_type)
            final_path = output_path.with_suffix(suffix)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            content = response.read()
            final_path.write_bytes(content)
    except (HTTPError, URLError, TimeoutError, OSError):
        return None

    if not valid_image(final_path):
        final_path.unlink(missing_ok=True)
        return None

    return final_path, hashlib.sha256(final_path.read_bytes()).hexdigest()


def iter_occurrence_media(
    scientific_name: str,
    *,
    page_size: int,
    allowed_license_tokens: tuple[str, ...],
    allow_all_licenses: bool,
    dataset_key: str | None,
    basis_of_record: str | None,
    max_images_per_occurrence: int,
):
    offset = 0
    seen_urls: set[str] = set()

    while True:
        params: dict[str, object] = {
            "scientificName": scientific_name,
            "mediaType": "StillImage",
            "limit": page_size,
            "offset": offset,
        }
        if dataset_key:
            params["datasetKey"] = dataset_key
        if basis_of_record:
            params["basisOfRecord"] = basis_of_record

        payload = fetch_json(
            GBIF_OCCURRENCE_SEARCH_URL,
            params,
        )
        results = payload.get("results", [])
        if not results:
            break

        for occurrence in results:
            media_items = occurrence.get("media") or []
            occurrence_media_count = 0
            for media_index, media in enumerate(media_items):
                if occurrence_media_count >= max_images_per_occurrence:
                    break

                image_url = media.get("identifier")
                if not image_url or image_url in seen_urls:
                    continue

                media_type = str(media.get("type") or "")
                if media_type and "StillImage" not in media_type:
                    continue

                license_value = str(media.get("license") or occurrence.get("license") or "")
                if not allow_all_licenses and not license_is_allowed(
                    license_value,
                    allowed_license_tokens,
                ):
                    continue

                seen_urls.add(image_url)
                occurrence_media_count += 1
                yield occurrence, media, media_index

        offset += page_size
        if offset >= int(payload.get("count", 0)):
            break


def build_demo_dataset(
    *,
    species_names: list[str],
    images_per_species: int,
    raw_images_dir: Path,
    raw_catalog_path: Path,
    species_seed_path: Path,
    sources_path: Path,
    page_size: int,
    sleep_seconds: float,
    allow_all_licenses: bool,
    dataset_key: str | None,
    basis_of_record: str | None,
    max_images_per_occurrence: int,
) -> dict[str, int]:
    rows: list[dict[str, object]] = []
    source_rows: list[dict[str, object]] = []
    summary: dict[str, int] = {}

    for scientific_name in species_names:
        code = species_code(scientific_name)
        species_dir = raw_images_dir / code
        downloaded = 0

        for occurrence, media, media_index in iter_occurrence_media(
            scientific_name,
            page_size=page_size,
            allowed_license_tokens=DEFAULT_LICENSE_TOKENS,
            allow_all_licenses=allow_all_licenses,
            dataset_key=dataset_key,
            basis_of_record=basis_of_record,
            max_images_per_occurrence=max_images_per_occurrence,
        ):
            if downloaded >= images_per_species:
                break

            gbif_key = str(occurrence.get("key") or f"missing_key_{downloaded}")
            base_name = f"gbif_{gbif_key}_{media_index}"
            downloaded_image = download_image(str(media.get("identifier")), species_dir / base_name)
            if downloaded_image is None:
                continue

            image_path, sha256 = downloaded_image
            occurrence_url = f"https://www.gbif.org/occurrence/{gbif_key}"
            source = occurrence.get("datasetName") or occurrence.get("publishingOrgKey") or "GBIF"
            row = {
                "image_id": image_path.stem,
                "specimen_id": occurrence.get("occurrenceID") or gbif_key,
                "species_code": code,
                "file_path": str(image_path.resolve()),
                "source": source,
                "view_type": "public_observation",
                "annotator": "GBIF community record",
                "label_status": "validated",
                "sha256": sha256,
                "scientific_name": scientific_name,
                "gbif_key": gbif_key,
                "occurrence_url": occurrence_url,
                "image_url": media.get("identifier"),
                "license": media.get("license") or occurrence.get("license") or "",
                "rights_holder": media.get("rightsHolder") or occurrence.get("rightsHolder") or "",
                "publisher": occurrence.get("publisher") or "",
                "dataset_name": occurrence.get("datasetName") or "",
            }
            rows.append(row)
            source_rows.append(row)
            downloaded += 1
            time.sleep(sleep_seconds)

        summary[scientific_name] = downloaded

    raw_catalog_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_catalog_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=RAW_CATALOG_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    species_seed_path.parent.mkdir(parents=True, exist_ok=True)
    with species_seed_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=["code", "scientific_name", "description"])
        writer.writeheader()
        for scientific_name in species_names:
            writer.writerow(
                {
                    "code": species_code(scientific_name),
                    "scientific_name": scientific_name,
                    "description": "Classe piloto baixada do GBIF para validacao tecnica do MVP.",
                }
            )

    sources_path.parent.mkdir(parents=True, exist_ok=True)
    with sources_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=RAW_CATALOG_COLUMNS)
        writer.writeheader()
        writer.writerows(source_rows)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a small GBIF image dataset for the Augochloropsis MVP demo."
    )
    parser.add_argument("--species", nargs="+", default=list(DEFAULT_SPECIES))
    parser.add_argument("--images-per-species", type=int, default=12)
    parser.add_argument("--raw-images-dir", type=Path, default=Path("../data/raw/images/gbif_demo"))
    parser.add_argument(
        "--raw-catalog",
        type=Path,
        default=Path("../data/raw/metadata/raw_catalog.csv"),
    )
    parser.add_argument(
        "--species-seed",
        type=Path,
        default=Path("../data/raw/metadata/species_seed.demo.csv"),
    )
    parser.add_argument(
        "--sources",
        type=Path,
        default=Path("../data/raw/metadata/gbif_demo_sources.csv"),
    )
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--sleep-seconds", type=float, default=0.3)
    parser.add_argument(
        "--dataset-key",
        type=str,
        default=None,
        help="Optional GBIF dataset key filter, e.g. iNaturalist research-grade observations.",
    )
    parser.add_argument(
        "--basis-of-record",
        type=str,
        default=None,
        help="Optional GBIF basisOfRecord filter, e.g. HUMAN_OBSERVATION.",
    )
    parser.add_argument("--max-images-per-occurrence", type=int, default=3)
    parser.add_argument(
        "--allow-all-licenses",
        action="store_true",
        help="Download images without filtering Creative Commons license tokens.",
    )
    args = parser.parse_args()

    summary = build_demo_dataset(
        species_names=args.species,
        images_per_species=args.images_per_species,
        raw_images_dir=args.raw_images_dir.resolve(),
        raw_catalog_path=args.raw_catalog.resolve(),
        species_seed_path=args.species_seed.resolve(),
        sources_path=args.sources.resolve(),
        page_size=args.page_size,
        sleep_seconds=args.sleep_seconds,
        allow_all_licenses=args.allow_all_licenses,
        dataset_key=args.dataset_key,
        basis_of_record=args.basis_of_record,
        max_images_per_occurrence=args.max_images_per_occurrence,
    )
    print(json.dumps({"downloaded": summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
