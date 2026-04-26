from __future__ import annotations

from functools import lru_cache

import numpy as np

from augochloropsis_ai.ml.preprocessing import load_pil_image_from_bytes


def _import_runtime_dependencies():
    try:
        import torch
        from transformers import AutoImageProcessor, AutoModel
    except ImportError as exc:
        raise RuntimeError("Transformers and PyTorch are required for embedding extraction.") from exc
    return torch, AutoImageProcessor, AutoModel


class DinoV2Embedder:
    def __init__(self, model_name: str = "facebook/dinov2-base") -> None:
        torch, AutoImageProcessor, AutoModel = _import_runtime_dependencies()
        self._torch = torch
        self.model_name = model_name
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed_bytes(self, content: bytes) -> np.ndarray:
        image = load_pil_image_from_bytes(content)
        inputs = self.processor(images=image, return_tensors="pt")
        with self._torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
        return embedding.astype(np.float32)


@lru_cache
def get_embedder(model_name: str) -> DinoV2Embedder:
    return DinoV2Embedder(model_name=model_name)
