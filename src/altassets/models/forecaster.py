"""Baseline sequence forecaster. Small enough to train on CPU."""

from __future__ import annotations

import torch
from torch import nn


class LSTMForecaster(nn.Module):
    def __init__(self, n_features: int, hidden: int = 64, layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(
            n_features, hidden, num_layers=layers, batch_first=True,
            dropout=dropout if layers > 1 else 0.0,
        )
        self.head = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return self.head(out[:, -1]).squeeze(-1)


def train(model, X, y, Xv, yv, epochs=50, lr=1e-3, batch_size=64, device=None):
    from altassets.models.device import get_device

    device = device or get_device()
    model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    X, y = torch.as_tensor(X), torch.as_tensor(y)
    Xv, yv = torch.as_tensor(Xv).to(device), torch.as_tensor(yv).to(device)
    history = []
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(len(X))
        for i in range(0, len(X), batch_size):
            idx = perm[i : i + batch_size]
            xb, yb = X[idx].to(device), y[idx].to(device)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            history.append(loss_fn(model(Xv), yv).item())
    return history
