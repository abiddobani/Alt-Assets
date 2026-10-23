"""Pick the best available device so the same code runs on a laptop CPU or a rented GPU."""

from __future__ import annotations

import os


def get_device(prefer: str | None = None):
    import torch

    prefer = prefer or os.environ.get("ALTASSETS_DEVICE")
    if prefer:
        return torch.device(prefer)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
