from __future__ import annotations

from functools import lru_cache
from typing import cast

import numpy as np

from augochloropsis_ai.ml.preprocessing import load_pil_image_from_bytes


def _import_runtime_dependencies():
    try:
        import torch
        from transformers import AutoImageProcessor, AutoModel
    except ImportError as exc:
        raise RuntimeError(
            "Transformers and PyTorch are required for embedding extraction."
        ) from exc
    return torch, AutoImageProcessor, AutoModel


class DinoEmbedder:
    def __init__(self, model_name: str = "facebook/dinov2-base") -> None:
        torch, AutoImageProcessor, AutoModel = _import_runtime_dependencies()
        self._torch = torch
        self.model_name = model_name
        try:
            self.processor = AutoImageProcessor.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        except OSError as exc:
            message = str(exc).lower()
            if "gated repo" in message or "401 client error" in message:
                raise RuntimeError(
                    "This encoder requires Hugging Face access. Accept the model terms and "
                    "authenticate with `huggingface-cli login` or set `HF_TOKEN`."
                ) from exc
            raise
        self.model.eval()

    def embed_bytes(self, content: bytes) -> np.ndarray:
        image = load_pil_image_from_bytes(content)
        inputs = self.processor(images=image, return_tensors="pt")
        with self._torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
        return cast(np.ndarray, embedding.astype(np.float32))


@lru_cache
def get_embedder(model_name: str) -> DinoEmbedder:
    return DinoEmbedder(model_name=model_name)
