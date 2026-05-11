from __future__ import annotations

from functools import lru_cache
from typing import Union, cast

import numpy as np

from beeai.ml.preprocessing import load_pil_image_from_bytes

_BIOCLIP_MODEL_ID = "hf-hub:imageomics/bioclip"
_BIOCLIP_HF_PREFIX = "imageomics/bioclip"


def _import_transformers():
    try:
        import torch
        from transformers import AutoImageProcessor, AutoModel
    except ImportError as exc:
        raise RuntimeError(
            "Transformers and PyTorch are required for embedding extraction."
        ) from exc
    return torch, AutoImageProcessor, AutoModel


def _import_open_clip():
    try:
        import open_clip
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "open_clip_torch is required for BioCLIP. "
            "Install with: pip install 'beeai[bioclip]' or pip install open_clip_torch"
        ) from exc
    return open_clip, torch


class DinoEmbedder:
    def __init__(self, model_name: str = "facebook/dinov2-base") -> None:
        torch, AutoImageProcessor, AutoModel = _import_transformers()
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
        embedding = self._extract_embedding(outputs).cpu().numpy()[0]
        return cast(np.ndarray, embedding.astype(np.float32))

    def _extract_embedding(self, outputs) -> "torch.Tensor":
        # ViT-based models (DINOv2, DINOv3 ViT): last_hidden_state is (batch, seq, dim)
        # position 0 is the class token
        if hasattr(outputs, "last_hidden_state") and outputs.last_hidden_state.ndim == 3:
            return outputs.last_hidden_state[:, 0, :]
        # ConvNeXt and other CNN models: pooler_output is the global-averaged feature vector
        if hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
            return outputs.pooler_output
        raise ValueError(
            f"Cannot extract embedding from model '{self.model_name}': "
            "expected last_hidden_state (ViT) or pooler_output (ConvNeXt)."
        )


class BioCLIPEmbedder:
    """Embedder for imageomics/bioclip using the open_clip library."""

    def __init__(self) -> None:
        open_clip, torch = _import_open_clip()
        self._torch = torch
        self.model_name = _BIOCLIP_HF_PREFIX
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            _BIOCLIP_MODEL_ID
        )
        self.model.eval()

    def embed_bytes(self, content: bytes) -> np.ndarray:
        image = load_pil_image_from_bytes(content)
        tensor = self.preprocess(image).unsqueeze(0)
        with self._torch.no_grad():
            features = self.model.encode_image(tensor)
        return cast(np.ndarray, features.cpu().numpy()[0].astype(np.float32))


@lru_cache
def get_embedder(model_name: str) -> Union[DinoEmbedder, BioCLIPEmbedder]:
    if model_name.startswith(_BIOCLIP_HF_PREFIX):
        return BioCLIPEmbedder()
    return DinoEmbedder(model_name=model_name)
