from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from augochloropsis_ai.ml.preprocessing import load_pil_image_from_bytes


def _import_runtime_dependencies():
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
    except ImportError as exc:
        message = "Transformers and PyTorch are required for global identification."
        raise RuntimeError(message) from exc
    return torch, CLIPModel, CLIPProcessor


@dataclass(frozen=True, slots=True)
class GlobalTaxonLabel:
    code: str
    scientific_name: str
    common_name: str

    @property
    def prompt(self) -> str:
        return f"a natural history photograph of {self.scientific_name}, {self.common_name}"


@dataclass(slots=True)
class GlobalIdentificationProbability:
    code: str
    scientific_name: str
    common_name: str
    probability: float


@dataclass(slots=True)
class GlobalIdentificationResult:
    predicted_code: str
    predicted_scientific_name: str
    predicted_common_name: str
    confidence: float
    probabilities: list[GlobalIdentificationProbability]
    model_name: str


DEFAULT_GLOBAL_LABELS = (
    GlobalTaxonLabel("aug_metallica", "Augochloropsis metallica", "green metallic sweat bee"),
    GlobalTaxonLabel("apis_mellifera", "Apis mellifera", "western honey bee"),
    GlobalTaxonLabel("bombus_impatiens", "Bombus impatiens", "common eastern bumble bee"),
    GlobalTaxonLabel("xylocopa_virginica", "Xylocopa virginica", "eastern carpenter bee"),
    GlobalTaxonLabel("halictus_ligatus", "Halictus ligatus", "sweat bee"),
    GlobalTaxonLabel("vespula_vulgaris", "Vespula vulgaris", "common wasp"),
    GlobalTaxonLabel("musca_domestica", "Musca domestica", "house fly"),
)


class ClipGlobalIdentifier:
    def __init__(
        self,
        *,
        model_name: str = "openai/clip-vit-base-patch32",
        labels: tuple[GlobalTaxonLabel, ...] = DEFAULT_GLOBAL_LABELS,
    ) -> None:
        torch, CLIPModel, CLIPProcessor = _import_runtime_dependencies()
        self._torch = torch
        self.model_name = model_name
        self.labels = labels
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name)
        self.model.eval()

    def identify_bytes(self, content: bytes) -> GlobalIdentificationResult:
        image = load_pil_image_from_bytes(content)
        prompts = [label.prompt for label in self.labels]
        inputs = self.processor(text=prompts, images=image, return_tensors="pt", padding=True)

        with self._torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]

        ordered_indices = np.argsort(probabilities)[::-1]
        ordered = [
            GlobalIdentificationProbability(
                code=self.labels[index].code,
                scientific_name=self.labels[index].scientific_name,
                common_name=self.labels[index].common_name,
                probability=float(probabilities[index]),
            )
            for index in ordered_indices
        ]
        top_prediction = ordered[0]

        return GlobalIdentificationResult(
            predicted_code=top_prediction.code,
            predicted_scientific_name=top_prediction.scientific_name,
            predicted_common_name=top_prediction.common_name,
            confidence=top_prediction.probability,
            probabilities=ordered,
            model_name=self.model_name,
        )


@lru_cache
def get_global_identifier(model_name: str = "openai/clip-vit-base-patch32") -> ClipGlobalIdentifier:
    return ClipGlobalIdentifier(model_name=model_name)
