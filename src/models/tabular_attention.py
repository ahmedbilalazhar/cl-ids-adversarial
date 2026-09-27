"""Tiny tabular Transformer (Phase-3 step 18, architecture sweep #3).

FT-Transformer-lite: shared linear feature projection -> 2-layer
TransformerEncoder -> mean pool -> linear head. Implements the SAME
interface as TabularMLP (classifier attr, expand_head with old-weight copy,
clone) so run_experiment / fedavg.py work unchanged (deepcopy +
load_state_dict). Deliberately small (d=64) for CPU parity with the MLP.
"""
from __future__ import annotations

import copy

import torch
import torch.nn as nn


class TabularTransformer(nn.Module):
    def __init__(
        self,
        in_dim: int,
        num_classes: int,
        d_model: int = 64,
        n_layers: int = 2,
        n_heads: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.proj(x).unsqueeze(1)  # (B, 1, d): one token per flow
        h = self.encoder(h).squeeze(1)
        return self.classifier(h)

    def expand_head(self, new_num_classes: int) -> None:
        if new_num_classes <= self.classifier.out_features:
            return
        old = self.classifier
        new = nn.Linear(old.in_features, new_num_classes)
        with torch.no_grad():
            new.weight[: old.out_features] = old.weight
            new.bias[: old.out_features] = old.bias
            nn.init.xavier_uniform_(new.weight[old.out_features :])
            new.bias[old.out_features :].zero_()
        self.classifier = new

    def clone(self) -> "TabularTransformer":
        return copy.deepcopy(self)
