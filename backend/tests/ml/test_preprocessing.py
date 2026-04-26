from __future__ import annotations

from io import BytesIO

from PIL import Image

from augochloropsis_ai.ml.preprocessing import load_pil_image_from_bytes


def test_load_pil_image_from_bytes_converts_to_rgb():
    buffer = BytesIO()
    Image.new("RGBA", (4, 4), color=(120, 180, 40, 255)).save(buffer, format="PNG")
    image = load_pil_image_from_bytes(buffer.getvalue())
    assert image.mode == "RGB"
    assert image.size == (4, 4)
