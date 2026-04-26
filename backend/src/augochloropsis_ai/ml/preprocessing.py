from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError

from augochloropsis_ai.core.exceptions import InvalidRequestError


def load_pil_image_from_bytes(content: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(content))
        image.load()
    except UnidentifiedImageError as exc:
        raise InvalidRequestError("The uploaded file is not a valid image.") from exc
    return image.convert("RGB")
