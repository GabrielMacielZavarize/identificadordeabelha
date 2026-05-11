from __future__ import annotations

from pathlib import Path


def _import_torch():
    try:
        import torch
        import torch.nn as nn
    except ImportError as exc:
        raise RuntimeError("PyTorch is required to load or run the classifier.") from exc
    return torch, nn


class MLPClassifier:
    def __new__(
        cls,
        *,
        input_dim: int,
        num_classes: int,
        hidden_dims: tuple[int, ...] = (256,),
        dropout: float = 0.2,
    ):
        _, nn = _import_torch()

        class _MLPClassifier(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                layers = []
                previous_dim = input_dim
                for hidden_dim in hidden_dims:
                    layers.extend(
                        [
                            nn.Linear(previous_dim, hidden_dim),
                            nn.ReLU(),
                            nn.Dropout(dropout),
                        ]
                    )
                    previous_dim = hidden_dim
                layers.append(nn.Linear(previous_dim, num_classes))
                self.network = nn.Sequential(*layers)

            def forward(self, inputs):
                return self.network(inputs)

        return _MLPClassifier()


def load_classifier_state(
    state_path: Path,
    *,
    input_dim: int,
    num_classes: int,
    hidden_dims: tuple[int, ...] = (256,),
    dropout: float = 0.2,
):
    torch, _ = _import_torch()
    classifier = MLPClassifier(
        input_dim=input_dim,
        num_classes=num_classes,
        hidden_dims=hidden_dims,
        dropout=dropout,
    )
    state = torch.load(state_path, map_location="cpu")
    classifier.load_state_dict(state)
    classifier.eval()
    return classifier


def predict_probabilities(classifier, embedding):
    torch, _ = _import_torch()
    tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        logits = classifier(tensor)
        probabilities = torch.softmax(logits, dim=-1)
    return probabilities.squeeze(0).cpu().numpy()
