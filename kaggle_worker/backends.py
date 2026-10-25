"""Small numerical port: orchestration is independent of CPU/CUDA adaptation."""
from __future__ import annotations

from typing import Any, Protocol

import numpy as np
import torch

from src.phase3_v2 import learning
from src.phase3.model import ReferenceMLP
from src.phase3_v2.data import StageInput
from src.phase3_v2.learning import ClientState
from src.phase3_v3.protocol import Settings

from .accelerator import Accelerator


class Backend(Protocol):
    def initialize_clients(self, clients: list[ClientState], settings: Settings) -> None: ...
    def admit(self, model: ReferenceMLP, data: StageInput, slots: list[int], new_codes: set[int],
              clients: list[ClientState], settings: Settings, ledger: list[dict[str, Any]]) -> np.ndarray: ...
    def train_client(self, broadcast: dict[str, torch.Tensor], template: ReferenceMLP, client: ClientState,
                     data: StageInput, slots: list[int], settings: Settings, round_id: int,
                     client_id: int) -> tuple[dict[str, torch.Tensor] | None, dict[str, Any]]: ...
    def importance(self, model: ReferenceMLP, clients: list[ClientState], data: StageInput, slots: list[int],
                   settings: Settings, ledger: list[dict[str, Any]]) -> None: ...


class CPUBackend:
    def initialize_clients(self, clients, settings):
        pass  # The original client factory already owns the CPU streams.

    admit = staticmethod(learning.admit)
    train_client = staticmethod(learning.train_client)
    importance = staticmethod(learning.commit_importance)


def backend_for(device, emulate_accelerator=False) -> Backend:
    if str(device).split(':')[0] == 'cuda' or emulate_accelerator:
        return Accelerator(device)
    if str(device) != 'cpu':
        raise ValueError('Unsupported numerical backend')
    return CPUBackend()
