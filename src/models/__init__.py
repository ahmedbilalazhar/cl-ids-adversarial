"""Model factory (Phase-3 step 18). cfg["arch"]: mlp (default) | wide | transformer."""
from __future__ import annotations

from src.models.mlp import TabularMLP
from src.models.tabular_attention import TabularTransformer


def build_model(cfg: dict, in_dim: int, n_classes: int):
    arch = str(cfg.get("arch", "mlp"))
    if arch == "mlp":
        return TabularMLP(in_dim, n_classes, hidden=cfg.get("hidden", [128, 64]))
    if arch == "wide":
        return TabularMLP(in_dim, n_classes, hidden=cfg.get("hidden", [256, 128]))
    if arch == "transformer":
        tcfg = cfg.get("transformer") or {}
        return TabularTransformer(
            in_dim,
            n_classes,
            d_model=int(tcfg.get("d_model", 64)),
            n_layers=int(tcfg.get("n_layers", 2)),
            n_heads=int(tcfg.get("n_heads", 4)),
        )
    raise ValueError(f"Unknown arch: {arch}")
