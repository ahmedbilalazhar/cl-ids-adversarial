"""Fresh-process synthetic recovery helper; no research package reader."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import configure
from .checks import fixtures
from .data import StageCache
from .simulator import execute
from src.phase3_v3.protocol import Settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--learner', choices=['FT', 'EI', 'DR'], required=True)
    parser.add_argument('--device', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resume', type=Path, required=True)
    parser.add_argument('--execution-json', required=True)
    args = parser.parse_args()
    configure(args.device)
    execute(Settings(args.learner, rounds=3, epochs=4), StageCache(fixtures().__getitem__),
            json.loads(args.execution_json), args.output, args.device, resume=args.resume)


if __name__ == '__main__':
    main()
