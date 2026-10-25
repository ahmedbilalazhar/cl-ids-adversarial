"""V3 study identity and prospective twelve-pass synchronization budgets."""
from __future__ import annotations

from dataclasses import dataclass

from src.phase3.common import ROOT, digest, identity, read_json
from src.phase3_v2.protocol import PROTOCOL as PARENT_PROTOCOL
from src.phase3_v2.protocol import Settings as ParentSettings
from src.phase3_v2.protocol import code_files as parent_files
from src.phase3_v2.protocol import code_identity as parent_identity
from src.phase3_v2.protocol import configure_runtime as parent_runtime

PROTOCOL = ROOT/'configs/phase3/cpu-v3.json'
DECISIONS = ROOT/'docs/phase3-cpu-v3/decisions-2026-10-24.md'
BUDGETS = ((3, 4), (12, 1))
COMPATIBILITY_BUDGETS = ((1, 3), (3, 1))


@dataclass(frozen=True)
class Settings(ParentSettings):
    rounds: int = 3
    epochs: int = 4

    def validate(self):
        # Delegate every unchanged restriction to the immutable parent validator.
        # Substitute only its supported budget for this validation call.
        values = {**self.__dict__, 'rounds': 3, 'epochs': 1}
        ParentSettings(**values).validate()
        if type(self.rounds) is not int or type(self.epochs) is not int or (self.rounds, self.epochs) not in BUDGETS+COMPATIBILITY_BUDGETS:
            raise ValueError('Only v3 pilots or explicit old-budget compatibility checks are supported')
        return self


def code_files():
    files = parent_files()
    files.update({p.relative_to(ROOT).as_posix(): digest(p) for p in sorted((ROOT/'src/phase3_v3').glob('*.py'))})
    return files


def code_identity():
    return identity(code_files())


def configure_runtime():
    config = read_json(PROTOCOL)
    if config['parent_code_identity'] != parent_identity() or config['runtime'] != read_json(PARENT_PROTOCOL)['runtime']:
        raise ValueError('V3 requires the unchanged accepted parent and pinned CPU runtime')
    return parent_runtime()
