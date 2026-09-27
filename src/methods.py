"""Registry of continual-learning methods.

Neutral home for the method map so federated runners don't have to import
the training CLI (``src.run_experiment``) to resolve a method name.
"""
from __future__ import annotations

from src.cl.base import limit_threads
from src.cl.derpp import DERpp
from src.cl.er import ExperienceReplay
from src.cl.ewc import EWC
from src.cl.finetune import FineTune
from src.cl.lwf import LwF

limit_threads()

METHODS = {
    "finetune": FineTune,
    "ewc": EWC,
    "lwf": LwF,
    "er": ExperienceReplay,
    "derpp": DERpp,
    "joint": FineTune,
}
